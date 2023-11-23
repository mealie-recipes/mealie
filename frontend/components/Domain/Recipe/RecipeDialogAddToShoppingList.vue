<template>
  <div v-if="dialog">
    <BaseDialog v-if="shoppingListDialog" v-model="dialog" :title="$t('recipe.add-to-list')" :icon="$globals.icons.cartCheck">
      <v-card-text>
        <v-card
          v-for="list in shoppingLists"
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
    </BaseDialog>
    <BaseDialog
      v-if="shoppingListIngredientDialog"
      v-model="dialog"
      :title="selectedShoppingList ? selectedShoppingList.name : $t('recipe.add-to-list')"
      :icon="$globals.icons.cartCheck"
      width="70%"
      :submit-text="$tc('recipe.add-to-list')"
      @submit="addRecipesToList()"
    >
      <div style="max-height: 70vh;  overflow-y: auto">
        <v-card
          v-for="(section, sectionIndex) in recipeIngredientSections" :key="section.recipeId + sectionIndex"
          elevation="0"
          height="fit-content"
          width="100%"
        >
          <v-divider v-if="sectionIndex > 0" class="mt-3" />
          <v-card-title
            v-if="recipeIngredientSections.length > 1"
            class="justify-center"
            width="100%"
          >
            <v-container style="width: 100%;">
              <v-row no-gutters class="ma-0 pa-0">
                <v-col cols="12" align-self="center" class="text-center">
                  {{ section.recipeName }}
                </v-col>
              </v-row>
              <v-row v-if="section.recipeScale > 1" no-gutters class="ma-0 pa-0">
                <!-- TODO: make this editable in the dialog and visible on single-recipe lists -->
                <v-col cols="12" align-self="center" class="text-center">
                  ({{ $tc("recipe.quantity") }}: {{ section.recipeScale }})
                </v-col>
              </v-row>
            </v-container>
          </v-card-title>
          <div
            :class="$vuetify.breakpoint.smAndDown ? '' : 'ingredient-grid'"
            :style="$vuetify.breakpoint.smAndDown ? '' : { gridTemplateRows: `repeat(${Math.ceil(section.ingredients.length / 2)}, min-content)` }"
          >
            <v-list-item
              v-for="(ingredientData, i) in section.ingredients"
              :key="'ingredient' + i"
              dense
              @click="recipeIngredientSections[sectionIndex].ingredients[i].checked = !recipeIngredientSections[sectionIndex].ingredients[i].checked"
            >
              <v-checkbox
                hide-details
                :input-value="ingredientData.checked"
                class="pt-0 my-auto py-auto"
                color="secondary"
              />
              <v-list-item-content :key="ingredientData.ingredient.quantity">
                <RecipeIngredientListItem
                  :ingredient="ingredientData.ingredient"
                  :disable-amount="ingredientData.disableAmount"
                  :scale="section.recipeScale" />
              </v-list-item-content>
            </v-list-item>
          </div>
        </v-card>
      </div>
      <div class="d-flex justify-end mb-4 mt-2">
        <BaseButtonGroup
          :buttons="[
            {
              icon: $globals.icons.checkboxBlankOutline,
              text: $tc('shopping-list.uncheck-all-items'),
              event: 'uncheck',
            },
            {
              icon: $globals.icons.checkboxOutline,
              text: $tc('shopping-list.check-all-items'),
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

<script lang="ts">
import { computed, defineComponent, reactive, ref, useContext } from "@nuxtjs/composition-api";
import { toRefs } from "@vueuse/core";
import RecipeIngredientListItem from "./RecipeIngredientListItem.vue";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { ShoppingListSummary } from "~/lib/api/types/group";
import { Recipe, RecipeIngredient } from "~/lib/api/types/recipe";

export interface RecipeWithScale extends Recipe {
  scale: number;
}

export interface ShoppingListRecipeIngredient {
  checked: boolean;
  ingredient: RecipeIngredient;
  disableAmount: boolean;
}

export interface ShoppingListRecipeIngredientSection {
  recipeId: string;
  recipeName: string;
  recipeScale: number;
  ingredients: ShoppingListRecipeIngredient[];
}

export default defineComponent({
  components: {
    RecipeIngredientListItem,
  },
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    recipes: {
      type: Array as () => RecipeWithScale[],
      default: undefined,
    },
    shoppingLists: {
      type: Array as () => ShoppingListSummary[],
      default: () => [],
    },
  },
  setup(props, context) {
    const { i18n } = useContext();
    const api = useUserApi();

    // v-model support
    const dialog = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
        initState();
      },
    });

    const state = reactive({
      shoppingListDialog: true,
      shoppingListIngredientDialog: false,
    });

    const recipeIngredientSections = ref<ShoppingListRecipeIngredientSection[]>([]);
    const selectedShoppingList = ref<ShoppingListSummary | null>(null);

    async function consolidateRecipesIntoSections(recipes: RecipeWithScale[]) {
      const recipeSectionMap = new Map<string, ShoppingListRecipeIngredientSection>();
      for (const recipe of recipes) {
        if (!recipe.slug) {
          continue;
        }

        if (recipeSectionMap.has(recipe.slug)) {
          // @ts-ignore not undefined, see above
          recipeSectionMap.get(recipe.slug).recipeScale += recipe.scale;
          continue;
        }

        if (!(recipe.id && recipe.name && recipe.recipeIngredient)) {
          const { data } = await api.recipes.getOne(recipe.slug);
          if (!data?.recipeIngredient?.length) {
            continue;
          }
          recipe.id = data.id || "";
          recipe.name = data.name || "";
          recipe.recipeIngredient = data.recipeIngredient;
        } else if (!recipe.recipeIngredient.length) {
          continue;
        }

        const shoppingListIngredients: ShoppingListRecipeIngredient[] = recipe.recipeIngredient.map((ing) => {
          return {
            checked: true,
            ingredient: ing,
            disableAmount: recipe.settings?.disableAmount || false,
          }
        });

        recipeSectionMap.set(recipe.slug, {
          recipeId: recipe.id,
          recipeName: recipe.name,
          recipeScale: recipe.scale,
          ingredients: shoppingListIngredients,
        })
      }

      recipeIngredientSections.value = Array.from(recipeSectionMap.values());
    }

    function initState() {
      state.shoppingListDialog = true;
      state.shoppingListIngredientDialog = false;
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

    function bulkCheckIngredients(value = true) {
      recipeIngredientSections.value.forEach((section) => {
        section.ingredients.forEach((ing) => {
          ing.checked = value;
        });
      });
    }

    async function addRecipesToList() {
      const promises: Promise<any>[] = [];
      recipeIngredientSections.value.forEach((section) => {
        if (!selectedShoppingList.value) {
          return;
        }

        const ingredients: RecipeIngredient[] = [];
        section.ingredients.forEach((ing) => {
          if (ing.checked) {
            ingredients.push(ing.ingredient);
          }
        });

        if (!ingredients.length) {
          return;
        }

        promises.push(api.shopping.lists.addRecipe(
          selectedShoppingList.value.id,
          section.recipeId,
          section.recipeScale,
          ingredients,
        ));
      });

      let success = true;
      const results = await Promise.allSettled(promises);
      results.forEach((result) => {
        if (result.status === "rejected") {
          success = false;
        }
      })

      success ? alert.success(i18n.t("recipe.recipes-added-to-list") as string)
      : alert.error(i18n.t("failed-to-add-recipes-to-list") as string)

      state.shoppingListDialog = false;
      state.shoppingListIngredientDialog = false;
      dialog.value = false;
    }

    return {
      dialog,
      ...toRefs(state),
      addRecipesToList,
      bulkCheckIngredients,
      openShoppingListIngredientDialog,
      recipeIngredientSections,
      selectedShoppingList,
    }
  },
})
</script>

<style scoped lang="css">
.ingredient-grid {
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: 1fr 1fr;
  grid-gap: 0.5rem;
}
</style>
