from uuid import uuid4

from slugify import slugify
from sqlalchemy import and_, update
from sqlalchemy.orm import Session

from mealie.core import root_logger
from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models.group.group import Group
from mealie.db.models.household.shopping_list import ShoppingList, ShoppingListMultiPurposeLabel
from mealie.db.models.labels import MultiPurposeLabel
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.users.users import User

logger = root_logger.get_logger("init_db")


def fix_dangling_refs(session: Session):
    REASSIGN_REF_TABLES = ["group_meal_plans", "recipes", "shopping_lists"]
    DELETE_REF_TABLES = ["long_live_tokens", "password_reset_tokens", "recipe_comments", "recipe_timeline_events"]

    all_groups = session.query(Group).all()
    all_users = session.query(User).all()
    for group in all_groups:
        # Find an arbitrary admin user in the group
        default_user = session.query(User).filter(User.group_id == group.id, User.admin == True).first()  # noqa: E712 - required for SQLAlchemy comparison
        if not default_user:
            # If there is no admin user, just pick the first user
            default_user = session.query(User).filter(User.group_id == group.id).first()

            # If there are no users in the group, we can't do anything
            if not default_user:
                continue

        valid_group_user_ids = {user.id for user in all_users if user.group_id == group.id}

        for table_name in REASSIGN_REF_TABLES:
            table = SqlAlchemyBase.metadata.tables[table_name]
            update_stmt = (
                update(table)
                .where(
                    and_(
                        table.c.user_id.notin_(valid_group_user_ids),
                        table.c.group_id == group.id,
                    )
                )
                .values(user_id=default_user.id)
            )
            result = session.execute(update_stmt)

            if result.rowcount:
                logger.info(
                    f"Reassigned {result.rowcount} {'row' if result.rowcount == 1 else 'rows'} "
                    f'in "{table_name}" table to default user ({default_user.id})'
                )

    valid_user_ids_all_groups = {user.id for user in all_users}
    for table_name in DELETE_REF_TABLES:
        table = SqlAlchemyBase.metadata.tables[table_name]
        delete_stmt = table.delete().where(table.c.user_id.notin_(valid_user_ids_all_groups))
        result = session.execute(delete_stmt)

        if result.rowcount:
            logger.info(
                f"Deleted {result.rowcount} {'row' if result.rowcount == 1 else 'rows'} "
                f'in "{table_name}" table with invalid user ids'
            )

    session.commit()


def fix_recipe_normalized_search_properties(session: Session):
    recipes = session.query(RecipeModel).all()
    recipes_fixed = False

    for recipe in recipes:
        add_to_session = False
        if recipe.name and not recipe.name_normalized:
            recipe.name_normalized = RecipeModel.normalize(recipe.name)
            add_to_session = True
        if recipe.description and not recipe.description_normalized:
            recipe.description_normalized = RecipeModel.normalize(recipe.description)
            add_to_session = True

        for ingredient in recipe.recipe_ingredient:
            if ingredient.note and not ingredient.note_normalized:
                ingredient.note_normalized = RecipeModel.normalize(ingredient.note)
                add_to_session = True
            if ingredient.original_text and not ingredient.original_text_normalized:
                ingredient.original_text = RecipeModel.normalize(ingredient.original_text_normalized)
                add_to_session = True

        if add_to_session:
            recipes_fixed = True
            session.add(recipe)

    if recipes_fixed:
        logger.info("Updating recipe normalized search properties")
        session.commit()


def fix_shopping_list_label_settings(session: Session):
    shopping_lists = session.query(ShoppingList).all()
    labels = session.query(MultiPurposeLabel).all()
    label_settings_fixed = False

    for shopping_list in shopping_lists:
        labels_by_id = {label.id: label for label in labels if label.group_id == shopping_list.group_id}
        for label_setting in shopping_list.label_settings:
            if not labels_by_id.pop(label_setting.label_id, None):
                # label setting is no longer valid, so delete it
                session.delete(label_setting)
                label_settings_fixed = True

        if not labels_by_id:
            # all labels are accounted for, so we don't need to add any
            continue

        label_settings_fixed = True
        for i, label in enumerate(labels_by_id.values()):
            new_label_setting = ShoppingListMultiPurposeLabel(
                id=uuid4(),
                shopping_list_id=shopping_list.id,
                label_id=label.id,
                position=i + len(shopping_list.label_settings),
            )

            session.add(new_label_setting)

    if label_settings_fixed:
        logger.info("Fixing shopping list label settings")
        session.commit()


def fix_group_slugs(session: Session):
    groups = session.query(Group).all()
    seen_slugs: set[str] = set()
    groups_fixed = False

    for group in groups:
        if not group.slug:
            original_name = group.name
            new_name = original_name
            attempts = 0
            while True:
                slug = slugify(group.name)
                if slug not in seen_slugs:
                    break

                attempts += 1
                new_name = f"{original_name} ({attempts})"

            groups_fixed = True
            group.name = new_name
            group.slug = slug

    if groups_fixed:
        logger.info("Adding missing group slugs")
        session.commit()


def fix_normalized_unit_and_food_names(session: Session):
    units = session.query(IngredientUnitModel).all()
    units_fixed = False

    for unit in units:
        add_to_session = False
        if unit.name and not unit.name_normalized:
            unit.name_normalized = IngredientUnitModel.normalize(unit.name)
            add_to_session = True
        if unit.abbreviation and not unit.abbreviation_normalized:
            unit.abbreviation_normalized = IngredientUnitModel.normalize(unit.abbreviation)
            add_to_session = True

        if add_to_session:
            units_fixed = True
            session.add(unit)

    if units_fixed:
        logger.info("Updating unit normalized search properties")
        session.commit()

    foods = session.query(IngredientFoodModel).all()
    foods_fixed = False

    for food in foods:
        add_to_session = False
        if food.name and not food.name_normalized:
            food.name_normalized = IngredientFoodModel.normalize(food.name)
            add_to_session = True

        if add_to_session:
            foods_fixed = True
            session.add(food)

    if foods_fixed:
        logger.info("Updating food normalized search properties")
        session.commit()


def fix_migration_data(session: Session):
    logger.info("Checking for migration data fixes")

    fix_dangling_refs(session)
    fix_recipe_normalized_search_properties(session)
    fix_shopping_list_label_settings(session)
    fix_group_slugs(session)
    fix_normalized_unit_and_food_names(session)
