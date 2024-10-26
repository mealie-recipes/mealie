<template>
  <div>
    <h2 class="mb-4">{{ $t("recipe.ingredients") }}</h2>
    <draggable
      v-if="recipe.recipeIngredient.length > 0"
      v-model="recipe.recipeIngredient"
      handle=".handle"
      delay="250"
      :delay-on-touch-only="true"
      v-bind="{
        animation: 200,
        group: 'recipe-ingredients',
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
          @insert-above="insertNewIngredient(index)"
          @insert-below="insertNewIngredient(index+1)"
        />
      </TransitionGroup>
    </draggable>
    <v-skeleton-loader v-else boilerplate elevation="2" type="list-item"> </v-skeleton-loader>
    <div class="d-flex flex-wrap justify-center justify-sm-end mt-3">
      <v-tooltip top color="accent">
        <template #activator="{ on, attrs }">
          <span v-on="on">
            <BaseButton
              class="mb-1"
              :disabled="recipe.settings.disableAmount || hasFoodOrUnit"
              color="accent"
              :to="`/g/${groupSlug}/r/${recipe.slug}/ingredient-parser`"
              v-bind="attrs"
            >
              <template #icon>
                {{ $globals.icons.foods }}
              </template>
              {{ $t('recipe.parse') }}
            </BaseButton>
          </span>
        </template>
        <span>{{ parserToolTip }}</span>
      </v-tooltip>
      <RecipeDialogBulkAdd class="mx-1 mb-1" @bulk-data="addIngredient" />
      <BaseButton class="mb-1" @click="addIngredient" > {{ $t("general.add") }} </BaseButton>
    </div>
  </div>
</template>

<script lang="ts">
import draggable from "vuedraggable";
import { computed, defineComponent, ref, useContext, useRoute } from "@nuxtjs/composition-api";
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
    const { $auth, i18n } = useContext();

    const drag = ref(false);

    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

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
        return i18n.t("recipe.enable-ingredient-amounts-to-use-this-feature");
      } else if (hasFoodOrUnit.value) {
        return i18n.t("recipe.recipes-with-units-or-foods-defined-cannot-be-parsed");
      }
      return i18n.t("recipe.parse-ingredients");
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

    function insertNewIngredient(dest: number) {
      props.recipe.recipeIngredient.splice(dest, 0, {
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

    return {
      user,
      groupSlug,
      addIngredient,
      parserToolTip,
      hasFoodOrUnit,
      imageKey,
      drag,
      insertNewIngredient,
    };
  },
});
</script>
