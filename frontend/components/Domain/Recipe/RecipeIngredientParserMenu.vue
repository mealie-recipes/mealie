<template>
  <div>
    <v-menu offset-y offset-overflow left top nudge-top="6" :close-on-content-click="false">
      <template #activator="{ on, attrs }">
        <v-btn color="accent" dark v-bind="attrs" v-on="on">
          <v-icon left>
            {{ $globals.icons.foods }}
          </v-icon>
          Parse
        </v-btn>
      </template>
      <v-card width="400">
        <v-card-title class="mb-1 pb-0"> Warning Experimental </v-card-title>
        <v-card-text>
          Mealie can use natural language processing to attempt to parse and create units, and foods for your Recipe
          ingredients. This is experimental and may not work as expected. If you choose to not use the parsed results
          you can click the close button at the top of the page and your changes will not be saved.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <BaseButton small color="accent" @click="parseIngredients">
            <template #icon>
              {{ $globals.icons.check }}
            </template>
            {{ $t("general.confirm") }}
          </BaseButton>
        </v-card-actions>
      </v-card>
    </v-menu>
    <BaseDialog ref="domParsedDataDialog" width="100%">
      <v-card-text>
        <div v-for="(ing, index) in parsedData.ingredient" :key="index">
          <div class="ml-10 text-body-1" :class="index > 0 ? 'mt-4' : null">{{ ingredients[index].note }}</div>
          <RecipeIngredientEditor :value="ing" />
        </div>
      </v-card-text>
    </BaseDialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import RecipeIngredientEditor from "./RecipeIngredientEditor.vue";
import { useApiSingleton } from "~/composables/use-api";
import { RecipeIngredient } from "~/types/api-types/recipe";

export default defineComponent({
  components: {
    RecipeIngredientEditor,
  },
  props: {
    ingredients: {
      type: Array,
      required: true,
    },
  },
  setup(props) {
    const ingredients = props.ingredients;
    const api = useApiSingleton();

    const parsedData = ref<any>([]);

    const domParsedDataDialog = ref(null);

    async function parseIngredients() {
      // @ts-ignore -> No idea what it's talking about
      const ingredientNotes = ingredients.map((ing: RecipeIngredient) => ing.note);

      const { data } = await api.recipes.parseIngredients(ingredientNotes);

      if (data) {
        // @ts-ignore
        domParsedDataDialog.value.open();
        console.log(data);
        parsedData.value = data;
      }

      console.log("ingredientNotes", ingredientNotes);
    }

    return { api, parseIngredients, parsedData, domParsedDataDialog };
  },
});
</script>
