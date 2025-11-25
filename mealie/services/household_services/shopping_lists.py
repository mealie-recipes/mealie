from typing import cast
import math

from pydantic import UUID4

from mealie.core.exceptions import UnexpectedNone
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.group_shopping_list import (
    ShoppingListAddRecipeParamsBulk,
    ShoppingListCreate,
    ShoppingListItemBase,
    ShoppingListItemCreate,
    ShoppingListItemOut,
    ShoppingListItemRecipeRefCreate,
    ShoppingListItemRecipeRefOut,
    ShoppingListItemsCollectionOut,
    ShoppingListItemUpdate,
    ShoppingListItemUpdateBulk,
    ShoppingListMultiPurposeLabelCreate,
    ShoppingListMultiPurposeLabelUpdate,
    ShoppingListOut,
    ShoppingListSave,
    ShoppingListSummary,
)
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import (
    IngredientFood,
    IngredientUnit,
    RecipeIngredient,
)
from mealie.schema.response.pagination import OrderDirection, PaginationQuery
from mealie.services.parser_services._base import DataMatcher
from mealie.schema.household.shopping_list_tesco import TescoBasketItem


class ShoppingListService:
    DEFAULT_FOOD_FUZZY_MATCH_THRESHOLD = 80

    def __init__(self, repos: AllRepositories):
        self.repos = repos
        self.shopping_lists = repos.group_shopping_lists
        self.list_items = repos.group_shopping_list_item
        self.list_item_refs = repos.group_shopping_list_item_references
        self.list_refs = repos.group_shopping_list_recipe_refs
        self.data_matcher = DataMatcher(self.repos, food_fuzzy_match_threshold=self.DEFAULT_FOOD_FUZZY_MATCH_THRESHOLD)

    @staticmethod
    def can_merge(item1: ShoppingListItemBase, item2: ShoppingListItemBase) -> bool:
        """Check to see if this item can be merged with another item"""

        if any(
            [
                item1.checked,
                item2.checked,
                item1.food_id != item2.food_id,
                item1.unit_id != item2.unit_id,
            ]
        ):
            return False

        # if foods match, we can merge, otherwise compare the notes
        return bool(item1.food_id) or item1.note == item2.note

    @staticmethod
    def merge_items(
        from_item: ShoppingListItemCreate | ShoppingListItemUpdateBulk,
        to_item: ShoppingListItemCreate | ShoppingListItemUpdateBulk | ShoppingListItemOut,
    ) -> ShoppingListItemUpdate:
        """
        Takes an item and merges it into an already-existing item, then returns a copy

        Attributes of the `to_item` take priority over the `from_item`, except extras with overlapping keys
        """

        to_item.quantity += from_item.quantity
        if to_item.note != from_item.note:
            to_item.note = " | ".join([note for note in [to_item.note, from_item.note] if note])

        if from_item.note and to_item.note != from_item.note:
            notes: set[str] = set(to_item.note.split(" | ")) if to_item.note else set()
            notes.add(from_item.note)
            to_item.note = " | ".join([note for note in notes if note])

        if to_item.extras and from_item.extras:
            to_item.extras.update(from_item.extras)

        updated_refs = {ref.recipe_id: ref for ref in from_item.recipe_references}
        for to_ref in to_item.recipe_references:
            if to_ref.recipe_id not in updated_refs:
                updated_refs[to_ref.recipe_id] = to_ref
                continue

            # merge recipe scales
            base_ref = updated_refs[to_ref.recipe_id]

            # if the scale is missing we assume it's 1 for backwards compatibility
            # if the scale is 0 we leave it alone
            if base_ref.recipe_scale is None:
                base_ref.recipe_scale = 1

            if to_ref.recipe_scale is None:
                to_ref.recipe_scale = 1

            base_ref.recipe_scale += to_ref.recipe_scale

        return to_item.cast(ShoppingListItemUpdate, recipe_references=list(updated_refs.values()))

    def remove_unused_recipe_references(self, shopping_list_id: UUID4) -> None:
        shopping_list = cast(ShoppingListOut, self.shopping_lists.get_one(shopping_list_id))

        recipe_ids_to_keep: set[UUID4] = set()
        for item in shopping_list.list_items:
            recipe_ids_to_keep.update([ref.recipe_id for ref in item.recipe_references])

        list_refs_to_delete: set[UUID4] = set()
        for list_ref in shopping_list.recipe_references:
            if list_ref.recipe_id not in recipe_ids_to_keep:
                list_refs_to_delete.add(list_ref.id)

        if list_refs_to_delete:
            self.list_refs.delete_many(list_refs_to_delete)

    def find_matching_label(self, item: ShoppingListItemBase) -> UUID4 | None:
        if item.label_id:
            return item.label_id
        if item.food:
            return item.food.label_id

        food_search = self.data_matcher.find_food_match(item.display)
        return food_search.label_id if food_search else None

    def bulk_create_items(
        self, create_items: list[ShoppingListItemCreate], auto_find_labels=True
    ) -> ShoppingListItemsCollectionOut:
        """
        Create a list of items, merging into existing ones where possible.
        Optionally try to find a label for each item if one isn't provided using the item's food data or display name.
        """

        # consolidate items to be created
        consolidated_create_items: list[ShoppingListItemCreate] = []
        for create_item in create_items:
            merged = False
            for i, filtered_item in enumerate(consolidated_create_items):
                if not self.can_merge(create_item, filtered_item):
                    continue

                consolidated_create_items[i] = self.merge_items(create_item, filtered_item).cast(ShoppingListItemCreate)
                merged = True
                break

            if not merged:
                consolidated_create_items.append(create_item)

        create_items = consolidated_create_items
        filtered_create_items: list[ShoppingListItemCreate] = []

        # check to see if we can merge into any existing items
        update_items: list[ShoppingListItemUpdateBulk] = []
        existing_items_map: dict[UUID4, list[ShoppingListItemOut]] = {}
        for create_item in create_items:
            if create_item.shopping_list_id not in existing_items_map:
                query = PaginationQuery(
                    per_page=-1, query_filter=f"shopping_list_id={create_item.shopping_list_id} AND checked=false"
                )
                items_data = self.list_items.page_all(query)
                existing_items_map[create_item.shopping_list_id] = items_data.items

            merged = False
            for existing_item in existing_items_map[create_item.shopping_list_id]:
                if not self.can_merge(existing_item, create_item):
                    continue

                updated_existing_item = self.merge_items(create_item, existing_item).cast(
                    ShoppingListItemUpdateBulk, id=existing_item.id
                )
                update_items.append(updated_existing_item.cast(ShoppingListItemUpdateBulk, id=existing_item.id))
                merged = True
                break

            if merged or create_item.quantity < 0:
                continue

            # create the item
            if create_item.checked:
                # checked items should not have recipe references
                create_item.recipe_references = []
            if auto_find_labels:
                create_item.label_id = self.find_matching_label(create_item)

            filtered_create_items.append(create_item)

        created_items = self.list_items.create_many(filtered_create_items) if filtered_create_items else []
        updated_items = self.list_items.update_many(update_items) if update_items else []

        for list_id in {item.shopping_list_id for item in created_items + updated_items}:
            self.remove_unused_recipe_references(list_id)

        return ShoppingListItemsCollectionOut(
            created_items=created_items, updated_items=updated_items, deleted_items=[]
        )

    def bulk_update_items(self, update_items: list[ShoppingListItemUpdateBulk]) -> ShoppingListItemsCollectionOut:
        # consolidate items to be created
        consolidated_update_items: list[ShoppingListItemUpdateBulk] = []
        delete_items: set[UUID4] = set()
        seen_update_ids: set[UUID4] = set()
        for update_item in update_items:
            # if the same item appears multiple times in one request, ignore all but the first instance
            if update_item.id in seen_update_ids:
                continue

            seen_update_ids.add(update_item.id)

            merged = False
            for i, filtered_item in enumerate(consolidated_update_items):
                if not self.can_merge(update_item, filtered_item):
                    continue

                consolidated_update_items[i] = self.merge_items(update_item, filtered_item).cast(
                    ShoppingListItemUpdateBulk, id=filtered_item.id
                )
                delete_items.add(update_item.id)
                merged = True
                break

            if not merged:
                consolidated_update_items.append(update_item)

        update_items = consolidated_update_items

        # check to see if we can merge into any existing items
        filtered_update_items: list[ShoppingListItemUpdateBulk] = []
        existing_items_map: dict[UUID4, list[ShoppingListItemOut]] = {}
        for update_item in update_items:
            if update_item.shopping_list_id not in existing_items_map:
                query = PaginationQuery(
                    per_page=-1, query_filter=f"shopping_list_id={update_item.shopping_list_id} AND checked=false"
                )
                items_data = self.list_items.page_all(query)
                existing_items_map[update_item.shopping_list_id] = items_data.items

            merged = False
            for existing_item in existing_items_map[update_item.shopping_list_id]:
                if existing_item.id in delete_items or existing_item.id == update_item.id:
                    continue

                if not self.can_merge(update_item, existing_item):
                    continue

                updated_existing_item = self.merge_items(update_item, existing_item).cast(
                    ShoppingListItemUpdateBulk, id=existing_item.id
                )
                filtered_update_items.append(updated_existing_item)
                delete_items.add(update_item.id)
                merged = True
                break

            if merged:
                continue

            # update or delete the item
            if update_item.quantity < 0:
                delete_items.add(update_item.id)
                continue

            if update_item.checked:
                # checked items should not have recipe references
                update_item.recipe_references = []

            filtered_update_items.append(update_item)

        updated_items = cast(
            list[ShoppingListItemOut],
            self.list_items.update_many(filtered_update_items) if filtered_update_items else [],  # type: ignore
        )

        deleted_items = cast(
            list[ShoppingListItemOut],
            self.list_items.delete_many(delete_items) if delete_items else [],  # type: ignore
        )

        for list_id in {item.shopping_list_id for item in updated_items + deleted_items}:
            self.remove_unused_recipe_references(list_id)

        return ShoppingListItemsCollectionOut(
            created_items=[], updated_items=updated_items, deleted_items=deleted_items
        )

    def bulk_delete_items(self, delete_items: list[UUID4]) -> ShoppingListItemsCollectionOut:
        deleted_items = cast(
            list[ShoppingListItemOut],
            self.list_items.delete_many(set(delete_items)) if delete_items else [],  # type: ignore
        )

        for list_id in {item.shopping_list_id for item in deleted_items}:
            self.remove_unused_recipe_references(list_id)

        return ShoppingListItemsCollectionOut(created_items=[], updated_items=[], deleted_items=deleted_items)

    def get_shopping_list_items_from_recipe(
        self,
        list_id: UUID4,
        recipe_id: UUID4,
        scale: float = 1,
        recipe_ingredients: list[RecipeIngredient] | None = None,
    ) -> list[ShoppingListItemCreate]:
        """Generates a list of new list items based on a recipe"""

        if recipe_ingredients is None:
            group_recipes_repo = get_repositories(
                self.repos.session, group_id=self.repos.group_id, household_id=None
            ).recipes
            recipe = group_recipes_repo.get_one(recipe_id, "id")
            if not recipe:
                raise UnexpectedNone("Recipe not found")

            recipe_ingredients = recipe.recipe_ingredient

        list_items: list[ShoppingListItemCreate] = []
        for ingredient in recipe_ingredients:
            if isinstance(ingredient.referenced_recipe, Recipe):
                # Recursively process sub-recipe ingredients
                sub_recipe = ingredient.referenced_recipe
                sub_scale = (ingredient.quantity or 1) * scale
                sub_items = self.get_shopping_list_items_from_recipe(
                    list_id,
                    sub_recipe.id,
                    sub_scale,
                    sub_recipe.recipe_ingredient,
                )
                list_items.extend(sub_items)
                continue

            if isinstance(ingredient.food, IngredientFood):
                food_id = ingredient.food.id
                label_id = ingredient.food.label_id
            else:
                food_id = None
                label_id = None

            if isinstance(ingredient.unit, IngredientUnit):
                unit_id = ingredient.unit.id

            else:
                unit_id = None

            new_item = ShoppingListItemCreate(
                shopping_list_id=list_id,
                note=ingredient.note,
                quantity=ingredient.quantity * scale if ingredient.quantity else 0,
                food_id=food_id,
                label_id=label_id,
                unit_id=unit_id,
                recipe_references=[
                    ShoppingListItemRecipeRefCreate(
                        recipe_id=recipe_id,
                        recipe_quantity=ingredient.quantity,
                        recipe_scale=scale,
                        recipe_note=ingredient.note or None,
                    )
                ],
            )

            # some recipes have the same ingredient multiple times, so we check to see if we can combine them
            merged = False
            for existing_item in list_items:
                if not self.can_merge(existing_item, new_item):
                    continue

                # since this is the same recipe, we combine the quanities, rather than the scales
                # all items will have exactly one recipe reference
                if ingredient.quantity:
                    existing_item.quantity += ingredient.quantity
                    existing_item.recipe_references[0].recipe_quantity += ingredient.quantity  # type: ignore

                # merge notes
                if new_item.note and existing_item.note != new_item.note:
                    notes: set[str] = set(existing_item.note.split(" | ")) if existing_item.note else set()
                    notes.add(new_item.note)
                    existing_item.note = " | ".join([note for note in notes if note])

                merged = True
                break

            if not merged:
                list_items.append(new_item)

        return list_items

    def add_recipe_ingredients_to_list(
        self,
        list_id: UUID4,
        recipe_items: list[ShoppingListAddRecipeParamsBulk],
    ) -> tuple[ShoppingListOut, ShoppingListItemsCollectionOut]:
        """
        Adds recipe ingredients to a list

        Returns a tuple of:
        - Updated Shopping List
        - Impacted Shopping List Items
        """

        items_to_create = [
            item
            for recipe in recipe_items
            for item in self.get_shopping_list_items_from_recipe(
                list_id, recipe.recipe_id, recipe.recipe_increment_quantity, recipe.recipe_ingredients
            )
        ]
        item_changes = self.bulk_create_items(items_to_create)
        updated_list = cast(ShoppingListOut, self.shopping_lists.get_one(list_id))

        # update list-level recipe references
        for recipe in recipe_items:
            ref_merged = False
            for ref in updated_list.recipe_references:
                if ref.recipe_id != recipe.recipe_id:
                    continue

                ref.recipe_quantity += recipe.recipe_increment_quantity
                ref_merged = True
                break

            if not ref_merged:
                updated_list.recipe_references.append(
                    ShoppingListItemRecipeRefCreate(
                        recipe_id=recipe.recipe_id, recipe_quantity=recipe.recipe_increment_quantity
                    )
                )

        updated_list = self.shopping_lists.update(updated_list.id, updated_list)
        return updated_list, item_changes

    def remove_recipe_ingredients_from_list(
        self, list_id: UUID4, recipe_id: UUID4, recipe_decrement: float = 1
    ) -> tuple[ShoppingListOut, ShoppingListItemsCollectionOut]:
        """
        Removes a recipe's ingredients from a list

        Returns a tuple of:
        - Updated Shopping List
        - Impacted Shopping List Items
        """

        shopping_list = self.shopping_lists.get_one(list_id)
        if shopping_list is None:
            raise UnexpectedNone("Shopping list not found, cannot remove recipe ingredients")

        update_items: list[ShoppingListItemUpdateBulk] = []
        delete_items: list[UUID4] = []
        for item in shopping_list.list_items:
            found = False

            refs = cast(list[ShoppingListItemRecipeRefOut], item.recipe_references)
            for ref in refs:
                if ref.recipe_id != recipe_id:
                    continue

                # if the scale is missing we assume it's 1 for backwards compatibility
                # if the scale is 0 we leave it alone
                if ref.recipe_scale is None:
                    ref.recipe_scale = 1

                # Set Quantity
                if ref.recipe_scale > recipe_decrement:
                    # remove only part of the reference
                    item.quantity -= recipe_decrement * ref.recipe_quantity

                else:
                    # remove everything that's left on the reference
                    item.quantity -= ref.recipe_scale * ref.recipe_quantity

                # Set Reference Scale
                ref.recipe_scale -= recipe_decrement
                if ref.recipe_scale <= 0:
                    item.recipe_references.remove(ref)

                found = True
                break

            if found:
                # only remove a 0 quantity item if we removed its last recipe reference
                if item.quantity < 0 or (item.quantity == 0 and not item.recipe_references):
                    delete_items.append(item.id)

                else:
                    update_items.append(item.cast(ShoppingListItemUpdateBulk))

        response_update = self.bulk_update_items(update_items)

        deleted_item_ids = [item.id for item in response_update.deleted_items]
        response_delete = self.bulk_delete_items([id for id in delete_items if id not in deleted_item_ids])

        items = ShoppingListItemsCollectionOut(
            created_items=response_update.created_items + response_delete.created_items,
            updated_items=response_update.updated_items + response_delete.updated_items,
            deleted_items=response_update.deleted_items + response_delete.deleted_items,
        )

        # Decrement the list recipe reference count
        updated_list = self.shopping_lists.get_one(shopping_list.id)
        for recipe_ref in updated_list.recipe_references:  # type: ignore
            if recipe_ref.recipe_id != recipe_id or recipe_ref.recipe_quantity is None:
                continue

            recipe_ref.recipe_quantity -= recipe_decrement

            if recipe_ref.recipe_quantity <= 0.0:
                self.list_refs.delete(recipe_ref.id)

            else:
                self.list_refs.update(recipe_ref.id, recipe_ref)

            break

        return self.shopping_lists.get_one(shopping_list.id), items  # type: ignore

    def create_one_list(self, data: ShoppingListCreate, owner_id: UUID4):
        create_data = data.cast(ShoppingListSave, group_id=self.repos.group_id, user_id=owner_id)
        new_list = self.shopping_lists.create(create_data)  # type: ignore

        labels = self.repos.group_multi_purpose_labels.page_all(
            PaginationQuery(page=1, per_page=-1, order_by="name", order_direction=OrderDirection.asc)
        )
        label_settings = [
            ShoppingListMultiPurposeLabelCreate(shopping_list_id=new_list.id, label_id=label.id, position=i)
            for i, label in enumerate(labels.items)
        ]

        self.repos.shopping_list_multi_purpose_labels.create_many(label_settings)
        return self.shopping_lists.get_one(new_list.id)

    def get_tesco_basket(self, list_id: UUID4) -> list[TescoBasketItem]:
        from mealie.core.config import get_app_settings
        import logging
        logger = logging.getLogger(__name__)
        
        shopping_list = self.shopping_lists.get_one(list_id)
        if not shopping_list:
            raise UnexpectedNone("Shopping list not found")

        logger.info(f"TESCO BASKET: Processing list {list_id} with {len(shopping_list.list_items)} items")

        # Collect all recipe IDs from the list items
        recipe_ids = set()
        for item in shopping_list.list_items:
            if item.checked:
                logger.info(f"TESCO BASKET: Skipping checked item {item.id}")
                continue
            for ref in item.recipe_references:
                recipe_ids.add(ref.recipe_id)

        if not recipe_ids:
            logger.info("TESCO BASKET: No recipe IDs found in list")
            return []

        logger.info(f"TESCO BASKET: Found recipe IDs: {recipe_ids}")

        # Fetch recipes
        # We fetch full recipes to ensure ingredients are loaded
        # Use existing repository with proper household context
        recipe_repo = self.repos.recipes
        logger.info(f"TESCO BASKET: Repo Context - Group ID: {self.repos.group_id}")
        
        recipe_map = {}
        for recipe_id in recipe_ids:
            try:
                recipe = recipe_repo.get_one(recipe_id, "id")
                if recipe:
                    recipe_map[recipe_id] = recipe
                    logger.info(f"TESCO BASKET: Loaded recipe {recipe.name} ({recipe.id}) with {len(recipe.recipe_ingredient)} ingredients")
                else:
                    logger.warning(f"TESCO BASKET: Recipe {recipe_id} returned None from repo")
            except Exception as e:
                logger.error(f"TESCO BASKET: Failed to load recipe {recipe_id}: {e}")
                continue

        basket_map = {}  # url -> dict

        # Helper to normalize text for comparison
        def normalize(text: str | None) -> str:
            return (text or "").lower().strip()

        # Helper to convert units
        def convert_quantity(qty: float, from_unit: str | None, to_unit: str | None) -> float:
            if not from_unit or not to_unit:
                return qty
            
            f = from_unit.lower().strip()
            t = to_unit.lower().strip()
            
            if f == t:
                return qty
            
            # Mass
            if f in ['g', 'gram', 'grams'] and t in ['kg', 'kilogram', 'kilograms']:
                return qty / 1000.0
            if f in ['kg', 'kilogram', 'kilograms'] and t in ['g', 'gram', 'grams']:
                return qty * 1000.0
            
            # Volume
            if f in ['ml', 'milliliter', 'milliliters'] and t in ['l', 'liter', 'liters']:
                return qty / 1000.0
            if f in ['l', 'liter', 'liters'] and t in ['ml', 'milliliter', 'milliliters']:
                return qty * 1000.0
                
            return qty

        for item in shopping_list.list_items:
            if item.checked:
                continue

            logger.debug(f"TESCO BASKET: Processing item {item.id}, Note: '{item.note}', FoodID: {item.food_id}")

            matched_via_recipe = False
            for ref in item.recipe_references:
                if ref.recipe_id not in recipe_map:
                    logger.debug(f"TESCO BASKET: Recipe {ref.recipe_id} not found in map")
                    continue
                
                recipe = recipe_map[ref.recipe_id]
                
                # Find the matching ingredient in the recipe
                matched_ingredient = None
                for ingredient in recipe.recipe_ingredient:
                    # 1. Match based on food and unit (if available)
                    if item.food_id and ingredient.food and ingredient.food.id:
                        if item.food_id == ingredient.food.id and item.unit_id == (ingredient.unit.id if ingredient.unit else None):
                            matched_ingredient = ingredient
                            logger.debug(f"TESCO BASKET: Matched by ID: {ingredient.reference_id}")
                            break
                    
                    # 2. Fallback: Match based on text (note vs original_text/title)
                    # This is needed when ingredients are not parsed into foods
                    if not item.food_id:
                        item_text = normalize(item.note)
                        ing_text = normalize(ingredient.original_text) or normalize(ingredient.title) or normalize(ingredient.note)
                        
                        logger.debug(f"TESCO BASKET: Comparing '{item_text}' vs '{ing_text}'")

                        # Simple containment check or exact match
                        if item_text and ing_text and (item_text == ing_text or item_text in ing_text or ing_text in item_text):
                            matched_ingredient = ingredient
                            logger.debug(f"TESCO BASKET: Matched by TEXT: {ingredient.reference_id}")
                            break
                
                if matched_ingredient:
                    if matched_ingredient.tesco_product_url:
                        url = matched_ingredient.tesco_product_url
                        logger.debug(f"TESCO BASKET: Found URL {url} for ingredient {matched_ingredient.reference_id}")
                        
                        if url not in basket_map:
                            basket_map[url] = {
                                "url": url,
                                "product_name": matched_ingredient.food.name if matched_ingredient.food else (matched_ingredient.title or matched_ingredient.note or "Unknown Product"),
                                "total_quantity_needed": 0.0,
                                "unit": matched_ingredient.tesco_units if matched_ingredient.tesco_units else (matched_ingredient.unit.name if matched_ingredient.unit else ""),
                                "pack_size": matched_ingredient.tesco_quantity or 1.0,
                                "estimated_cost": matched_ingredient.tesco_price or 0.0,
                                "tesco_units": matched_ingredient.tesco_units
                            }
                        
                        # Use the item's total quantity instead of recalculating from references
                        qty_to_add = item.quantity
                        
                        # Unit conversion
                        recipe_unit = matched_ingredient.unit.name if matched_ingredient.unit else None
                        tesco_unit = matched_ingredient.tesco_units
                        
                        if tesco_unit:
                            qty_to_add = convert_quantity(qty_to_add, recipe_unit, tesco_unit)
                            
                        basket_map[url]["total_quantity_needed"] += qty_to_add
                        matched_via_recipe = True
                        break 
                    else:
                        logger.debug(f"TESCO BASKET: Matched ingredient {matched_ingredient.reference_id} has no Tesco URL")
                else:
                    logger.debug(f"TESCO BASKET: No match found for item {item.id} in recipe {recipe.id}")

            # If not matched via recipe (or no recipe refs), try manual food link
            if not matched_via_recipe and item.food and item.food.tesco_product_url:
                url = item.food.tesco_product_url
                logger.debug(f"TESCO BASKET: Found Manual URL {url} for item {item.id}")
                
                if url not in basket_map:
                    basket_map[url] = {
                        "url": url,
                        "product_name": item.food.name,
                        "total_quantity_needed": 0.0,
                        "unit": item.food.tesco_units if item.food.tesco_units else (item.unit.name if item.unit else ""),
                        "pack_size": item.food.tesco_quantity or 1.0,
                        "estimated_cost": item.food.tesco_price or 0.0,
                        "tesco_units": item.food.tesco_units
                    }
                
                qty_to_add = item.quantity
                
                # Unit conversion for manual items
                item_unit = item.unit.name if item.unit else None
                tesco_unit = item.food.tesco_units
                
                if tesco_unit:
                    qty_to_add = convert_quantity(qty_to_add, item_unit, tesco_unit)
                    
                basket_map[url]["total_quantity_needed"] += qty_to_add

        basket_items = []
        for url, data in basket_map.items():
            pack_size = data["pack_size"]
            # Avoid division by zero
            if pack_size <= 0:
                pack_size = 1.0
            
            packs = math.ceil(data["total_quantity_needed"] / pack_size)
            
            basket_items.append(TescoBasketItem(
                url=url,
                product_name=data["product_name"],
                total_quantity_needed=data["total_quantity_needed"],
                unit=data["unit"],
                pack_size=pack_size,
                packs_needed=packs,
                estimated_cost=packs * data["estimated_cost"]
            ))
            
        logger.info(f"TESCO BASKET: Returning {len(basket_items)} items")
        return basket_items

