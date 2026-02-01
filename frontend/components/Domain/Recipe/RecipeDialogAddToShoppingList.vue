<template>
  <div v-if="dialog">
    <BaseDialog
      v-if="shoppingListDialog && ready"
      v-model="dialog"
      :title="$t('recipe.add-to-list')"
      :icon="$globals.icons.cartCheck"
    >
      <v-container v-if="!filteredShoppingLists.length">
        <BasePageTitle>
          <template #title>
            {{ $t('shopping-list.no-shopping-lists-found') }}
          </template>
        </BasePageTitle>
      </v-container>
      <v-card-text>
        <v-card
          v-for="list in filteredShoppingLists"
          :key="list.id"
          hover
          class="my-2 left-border"
          @click="openShoppingListIngredientDialog(list)"
        >
          <v-card-title class="py-2">
            {{ list.name }}
          </v-card-title>
        </v-card>
      </v-card-text>
      <template #card-actions>
        <v-btn
          variant="text"
          color="grey"
          @click="dialog = false"
        >
          {{ $t("general.cancel") }}
        </v-btn>
        <div
          class="d-flex justify-end"
          style="width: 100%;"
        >
          <v-checkbox
            v-model="preferences.viewAllLists"
            hide-details
            :label="$t('general.show-all')"
            class="my-auto mr-4"
            @click="setShowAllToggled()"
          />
        </div>
      </template>
    </BaseDialog>
    <BaseDialog
      v-if="shoppingListIngredientDialog"
      v-model="dialog"
      :title="selectedShoppingList?.name || $t('recipe.add-to-list')"
      :icon="$globals.icons.cartCheck"
      width="70%"
      :submit-text="$t('recipe.add-to-list')"
      can-submit
      @submit="addRecipesToList()"
    >
      <div style="max-height: 70vh;  overflow-y: auto">
        <v-card
          v-for="(recipeSection, recipeSectionIndex) in recipeIngredientSections"
          :key="recipeSection.recipeId + recipeSectionIndex"
          elevation="0"
          height="fit-content"
          width="100%"
        >
          <v-divider
            v-if="recipeSectionIndex > 0"
            class="mt-3"
          />
          <v-card-title
            v-if="recipeIngredientSections.length > 1"
            class="justify-center text-h5"
            width="100%"
          >
            <v-container style="width: 100%;">
              <v-row
                no-gutters
                class="ma-0 pa-0"
              >
                <v-col
                  cols="12"
                  align-self="center"
                  class="text-center"
                >
                  {{ recipeSection.recipeName }}
                </v-col>
              </v-row>
              <v-row
                v-if="recipeSection.recipeScale > 1"
                no-gutters
                class="ma-0 pa-0"
              >
                <!-- TODO: make this editable in the dialog and visible on single-recipe lists -->
                <v-col
                  cols="12"
                  align-self="center"
                  class="text-center"
                >
                  ({{ $t("recipe.quantity") }}: {{ recipeSection.recipeScale }})
                </v-col>
              </v-row>
            </v-container>
          </v-card-title>
          <div>
            <div
              v-for="(ingredientSection, ingredientSectionIndex) in recipeSection.ingredientSections"
              :key="recipeSection.recipeId + recipeSectionIndex + ingredientSectionIndex"
            >
              <v-card-title
                v-if="ingredientSection.sectionName"
                class="ingredient-title mt-2 pb-0 text-h6"
              >
                {{ ingredientSection.sectionName }}
              </v-card-title>
              <div
                :class="$vuetify.display.smAndDown ? '' : 'ingredient-grid'"
                :style="$vuetify.display.smAndDown ? '' : { gridTemplateRows: `repeat(${Math.ceil(ingredientSection.ingredients.length / 2)}, min-content)` }"
              >
                <v-list-item
                  v-for="(ingredientData, i) in ingredientSection.ingredients"
                  :key="recipeSection.recipeId + recipeSectionIndex + ingredientSectionIndex + i"
                  density="compact"
                  @click="recipeIngredientSections[recipeSectionIndex]
                    .ingredientSections[ingredientSectionIndex]
                    .ingredients[i].checked = !recipeIngredientSections[recipeSectionIndex]
                      .ingredientSections[ingredientSectionIndex]
                      .ingredients[i]
                      .checked"
                >
                  <v-container class="pa-0 ma-0">
                    <v-row no-gutters>
                      <v-checkbox
                        hide-details
                        :model-value="ingredientData.checked"
                        class="pt-0 my-auto py-auto mr-2"
                        color="secondary"
                        density="compact"
                      />
                      <div :key="`${ingredientData.ingredient?.quantity || 'no-qty'}-${i}`" class="pa-auto my-auto">
                        <RecipeIngredientListItem
                          :ingredient="ingredientData.ingredient"
                          :scale="recipeSection.recipeScale"
                        />
                      </div>
                    </v-row>
                  </v-container>
                </v-list-item>
              </div>
            </div>
          </div>
        </v-card>
      </div>
      <div class="d-flex justify-end mb-4 mt-2">
        <BaseButtonGroup
          :buttons="[
            {
              icon: $globals.icons.checkboxBlankOutline,
              text: $t('shopping-list.uncheck-all-items'),
              event: 'uncheck',
            },
            {
              icon: $globals.icons.checkboxOutline,
              text: $t('shopping-list.check-all-items'),
              event: 'check',
            },
          ]"
          @uncheck="bulkCheckIngredients(false)"
          @check="bulkCheckIngredients(true)"
        />
      </div>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { toRefs } from "@vueuse/core";
import RecipeIngredientListItem from "./RecipeIngredientListItem.vue";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { useShoppingListPreferences } from "~/composables/use-users/preferences";
import type { RecipeIngredient, ShoppingListAddRecipeParamsBulk, ShoppingListSummary } from "~/lib/api/types/household";
import type { Recipe } from "~/lib/api/types/recipe";

export interface RecipeWithScale extends Recipe {
  scale: number;
}

export interface ShoppingListIngredient {
  checked: boolean;
  ingredient: RecipeIngredient;
}

export interface ShoppingListIngredientSection {
  sectionName: string;
  ingredients: ShoppingListIngredient[];
}

export interface ShoppingListRecipeIngredientSection {
  recipeId: string;
  recipeName: string;
  recipeScale: number;
  ingredientSections: ShoppingListIngredientSection[];
}

interface Props {
  recipes?: RecipeWithScale[];
  shoppingLists?: ShoppingListSummary[];
}
const props = withDefaults(defineProps<Props>(), {
  recipes: undefined,
  shoppingLists: () => [],
});

const dialog = defineModel<boolean>({ default: false });

const i18n = useI18n();
const $auth = useMealieAuth();
const api = useUserApi();
const preferences = useShoppingListPreferences();
const ready = ref(false);

// Capture values at initialization to avoid reactive updates
const currentHouseholdSlug = ref("");
const filteredShoppingLists = ref<ShoppingListSummary[]>([]);

const state = reactive({
  shoppingListDialog: true,
  shoppingListIngredientDialog: false,
  shoppingListShowAllToggled: false,
});

const { shoppingListDialog, shoppingListIngredientDialog, shoppingListShowAllToggled: _shoppingListShowAllToggled } = toRefs(state);

const recipeIngredientSections = ref<ShoppingListRecipeIngredientSection[]>([]);
const selectedShoppingList = ref<ShoppingListSummary | null>(null);

watch([dialog, () => preferences.value.viewAllLists], () => {
  if (dialog.value) {
    currentHouseholdSlug.value = $auth.user.value?.householdSlug || "";
    filteredShoppingLists.value = props.shoppingLists.filter(
      list => preferences.value.viewAllLists || list.userId === $auth.user.value?.id,
    );

    if (filteredShoppingLists.value.length === 1 && !state.shoppingListShowAllToggled) {
      selectedShoppingList.value = filteredShoppingLists.value[0];
      openShoppingListIngredientDialog(selectedShoppingList.value);
    }
    else {
      ready.value = true;
    }
  }
  else if (!dialog.value) {
    initState();
  }
});

async function consolidateRecipesIntoSections(recipes: RecipeWithScale[]) {
  const recipeSectionMap = new Map<string, ShoppingListRecipeIngredientSection>();
  for (const recipe of recipes) {
    if (!recipe.slug) {
      continue;
    }

    if (recipeSectionMap.has(recipe.slug)) {
      const existingSection = recipeSectionMap.get(recipe.slug);
      if (existingSection) {
        existingSection.recipeScale += recipe.scale;
      }
      continue;
    }

    // Create a local copy to avoid mutating props
    let recipeData = { ...recipe };
    if (!(recipeData.id && recipeData.name && recipeData.recipeIngredient)) {
      const { data } = await api.recipes.getOne(recipeData.slug);
      if (!data?.recipeIngredient?.length) {
        continue;
      }
      recipeData = {
        ...recipeData,
        id: data.id || "",
        name: data.name || "",
        recipeIngredient: data.recipeIngredient,
      };
    }
    else if (!recipeData.recipeIngredient.length) {
      continue;
    }

    const shoppingListIngredients: ShoppingListIngredient[] = [];
    function flattenRecipeIngredients(ing: RecipeIngredient, parentTitle = ""): ShoppingListIngredient[] {
      if (ing.referencedRecipe) {
        // Recursively flatten all ingredients in the referenced recipe
        return (ing.referencedRecipe.recipeIngredient ?? []).flatMap((subIng) => {
          const calculatedQty = (ing.quantity || 1) * (subIng.quantity || 1);
          // Pass the referenced recipe name as the section title
          return flattenRecipeIngredients(
            { ...subIng, quantity: calculatedQty },
            "",
          );
        });
      }
      else {
        // Regular ingredient
        const householdsWithFood = ing.food?.householdsWithIngredientFood || [];
        return [{
          checked: !householdsWithFood.includes(currentHouseholdSlug.value),
          ingredient: {
            ...ing,
            title: ing.title || parentTitle,
          },
        }];
      }
    }

    recipeData.recipeIngredient.forEach((ing) => {
      const flattened = flattenRecipeIngredients(ing, "");
      shoppingListIngredients.push(...flattened);
    });

    let currentTitle = "";
    const onHandIngs: ShoppingListIngredient[] = [];
    const shoppingListIngredientSections = shoppingListIngredients.reduce((sections, ing) => {
      if (ing.ingredient.title) {
        currentTitle = ing.ingredient.title;
      }
      else if (ing.ingredient.referencedRecipe?.name) {
        currentTitle = ing.ingredient.referencedRecipe.name;
      }

      // If this is the first item in the section, create a new section
      if (sections.length === 0 || currentTitle !== sections[sections.length - 1].sectionName) {
        if (sections.length) {
          // Add the on-hand ingredients to the previous section
          sections[sections.length - 1].ingredients.push(...onHandIngs);
          onHandIngs.length = 0;
        }
        sections.push({
          sectionName: currentTitle,
          ingredients: [],
        });
      }

      // Store the on-hand ingredients for later
      const householdsWithFood = (ing.ingredient?.food?.householdsWithIngredientFood || []);
      if (householdsWithFood.includes(currentHouseholdSlug.value)) {
        onHandIngs.push(ing);
        return sections;
      }

      // Add the ingredient to previous section
      sections[sections.length - 1].ingredients.push(ing);
      return sections;
    }, [] as ShoppingListIngredientSection[]);

    // Add remaining on-hand ingredients to the previous section
    shoppingListIngredientSections[shoppingListIngredientSections.length - 1].ingredients.push(...onHandIngs);

    recipeSectionMap.set(recipe.slug, {
      recipeId: recipeData.id,
      recipeName: recipeData.name,
      recipeScale: recipeData.scale,
      ingredientSections: shoppingListIngredientSections,
    });
  }

  recipeIngredientSections.value = Array.from(recipeSectionMap.values());
}

function initState() {
  state.shoppingListDialog = true;
  state.shoppingListIngredientDialog = false;
  state.shoppingListShowAllToggled = false;
  recipeIngredientSections.value = [];
  selectedShoppingList.value = null;
}

initState();

async function openShoppingListIngredientDialog(list: ShoppingListSummary) {
  if (!props.recipes?.length) {
    return;
  }

  selectedShoppingList.value = list;
  await consolidateRecipesIntoSections(props.recipes);
  state.shoppingListDialog = false;
  state.shoppingListIngredientDialog = true;
}

function setShowAllToggled() {
  state.shoppingListShowAllToggled = true;
}

function bulkCheckIngredients(value = true) {
  recipeIngredientSections.value.forEach((recipeSection) => {
    recipeSection.ingredientSections.forEach((ingSection) => {
      ingSection.ingredients.forEach((ing) => {
        ing.checked = value;
      });
    });
  });
}

async function addRecipesToList() {
  if (!selectedShoppingList.value) {
    return;
  }

  const recipeData: ShoppingListAddRecipeParamsBulk[] = [];
  recipeIngredientSections.value.forEach((section) => {
    const ingredients: RecipeIngredient[] = [];
    section.ingredientSections.forEach((ingSection) => {
      ingSection.ingredients.forEach((ing) => {
        if (ing.checked) {
          ingredients.push(ing.ingredient);
        }
      });
    });

    if (!ingredients.length) {
      return;
    }

    recipeData.push(
      {
        recipeId: section.recipeId,
        recipeIncrementQuantity: section.recipeScale,
        recipeIngredients: ingredients,
      },
    );
  });

  const { error } = await api.shopping.lists.addRecipes(selectedShoppingList.value.id, recipeData);
  // eslint-disable-next-line @typescript-eslint/no-unused-expressions
  error ? alert.error(i18n.t("recipe.failed-to-add-recipes-to-list")) : alert.success(i18n.t("recipe.successfully-added-to-list"));

  state.shoppingListDialog = false;
  state.shoppingListIngredientDialog = false;
  dialog.value = false;
}
</script>

<style scoped lang="css">
.ingredient-grid {
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: 1fr 1fr;
  grid-gap: 0.5rem;
}
</style>
