<template>
  <div>
    <h2 class="mb-4">{{ $t("recipe.ingredients") }}</h2>
    <draggable
      v-if="recipe.recipeIngredient.length > 0"
      v-model="recipe.recipeIngredient"
      handle=".handle"
      v-bind="{
        animation: 200,
        group: 'description',
        disabled: false,
        ghostClass: 'ghost',
      }"
      @start="drag = true"
      @end="drag = false"
    >
      <TransitionGroup type="transition" :name="!drag ? 'flip-list' : ''">
        <RecipeIngredientEditor
          v-for="(ingredient, index) in recipe.recipeIngredient"
          :key="ingredient.referenceId"
          v-model="recipe.recipeIngredient[index]"
          class="list-group-item"
          :disable-amount="recipe.settings.disableAmount"
          @delete="recipe.recipeIngredient.splice(index, 1)"
        />
      </TransitionGroup>
    </draggable>
    <v-skeleton-loader v-else boilerplate elevation="2" type="list-item"> </v-skeleton-loader>
    <div class="d-flex justify-end mt-2">
      <v-tooltip top color="accent">
        <template #activator="{ on, attrs }">
          <span v-on="on">
            <BaseButton
              :disabled="recipe.settings.disableAmount || hasFoodOrUnit"
              color="accent"
              :to="`${recipe.slug}/ingredient-parser`"
              v-bind="attrs"
            >
              <template #icon>
                {{ $globals.icons.foods }}
              </template>
              Parse
            </BaseButton>
          </span>
        </template>
        <span>{{ parserToolTip }}</span>
      </v-tooltip>
      <RecipeDialogBulkAdd class="ml-1 mr-1" @bulk-data="addIngredient" />
      <BaseButton @click="addIngredient"> {{ $t("general.new") }} </BaseButton>
    </div>
  </div>
</template>

<script lang="ts">
import draggable from "vuedraggable";
import { computed, defineComponent, ref } from "@nuxtjs/composition-api";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
import RecipeIngredientEditor from "~/components/Domain/Recipe/RecipeIngredientEditor.vue";
import RecipeDialogBulkAdd from "~/components/Domain/Recipe/RecipeDialogBulkAdd.vue";
import { uuid4 } from "~/composables/use-utils";
export default defineComponent({
  components: {
    draggable,
    RecipeDialogBulkAdd,
    RecipeIngredientEditor,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const { user } = usePageUser();
    const { imageKey } = usePageState(props.recipe.slug);

    const drag = ref(false);

    const hasFoodOrUnit = computed(() => {
      if (!props.recipe) {
        return false;
      }
      if (props.recipe.recipeIngredient) {
        for (const ingredient of props.recipe.recipeIngredient) {
          if (ingredient.food || ingredient.unit) {
            return true;
          }
        }
      }

      return false;
    });

    const parserToolTip = computed(() => {
      if (props.recipe.settings.disableAmount) {
        return "Enable ingredient amounts to use this feature";
      } else if (hasFoodOrUnit.value) {
        return "Recipes with units or foods defined cannot be parsed.";
      }
      return "Parse ingredients";
    });

    function addIngredient(ingredients: Array<string> | null = null) {
      if (ingredients?.length) {
        const newIngredients = ingredients.map((x) => {
          return {
            referenceId: uuid4(),
            title: "",
            note: x,
            unit: undefined,
            food: undefined,
            disableAmount: true,
            quantity: 1,
          };
        });

        if (newIngredients) {
          // @ts-expect-error - prop can be null-type by NoUndefinedField type forces it to be set
          props.recipe.recipeIngredient.push(...newIngredients);
        }
      } else {
        props.recipe.recipeIngredient.push({
          referenceId: uuid4(),
          title: "",
          note: "",
          // @ts-expect-error - prop can be null-type by NoUndefinedField type forces it to be set
          unit: undefined,
          // @ts-expect-error - prop can be null-type by NoUndefinedField type forces it to be set
          food: undefined,
          disableAmount: true,
          quantity: 1,
        });
      }
    }

    return {
      user,
      addIngredient,
      parserToolTip,
      hasFoodOrUnit,
      imageKey,
      drag,
    };
  },
});
</script>
