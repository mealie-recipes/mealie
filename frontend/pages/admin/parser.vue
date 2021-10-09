<template>
  <v-container>
    <v-container>
      <BaseCardSectionTitle title="Ingredients Natural Language Processor">
        Mealie uses conditional random Conditional Random Fields (CRFs) for parsing and processing ingredients. The
        model used for ingredients is based off a data set of over 100,000 ingredients from a dataset compiled by the
        New York Times. Note that as the model is trained in English only, you may have varied results when using the
        model in other languages. This page is a playground for testing the model.

        <p class="pt-3">
          It's not perfect, but it yields great results in general and is a good starting point for manually parsing
          ingredients into individual fields.
        </p>
      </BaseCardSectionTitle>

      <v-card flat>
        <v-card-text>
          <v-text-field v-model="ingredient" label="Ingredient Text"> </v-text-field>
        </v-card-text>
        <v-card-actions>
          <BaseButton class="ml-auto" @click="processIngredient">
            <template #icon> {{ $globals.icons.check }}</template>
            {{ $t("general.submit") }}
          </BaseButton>
        </v-card-actions>
      </v-card>
    </v-container>
    <v-container v-if="results">
      <v-row class="d-flex">
        <template v-for="(prop, index) in properties">
          <v-col v-if="prop.value" :key="index" xs="12" sm="6" lg="3">
            <v-card>
              <v-card-title> {{ prop.value }} </v-card-title>
              <v-card-text>
                {{ prop.subtitle }}
              </v-card-text>
            </v-card>
          </v-col>
        </template>
      </v-row>
    </v-container>
    <v-container class="narrow-container">
      <v-card-title> Try an example </v-card-title>

      <v-card v-for="(text, idx) in tryText" :key="idx" class="my-2" hover @click="processTryText(text)">
        <v-card-text> {{ text }} </v-card-text>
      </v-card>
    </v-container>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent, reactive, toRefs } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";

export default defineComponent({
  layout: "admin",
  setup() {
    const api = useApiSingleton();

    const state = reactive({
      loading: false,
      ingredient: "",
      results: false,
    });

    const tryText = [
      "2 tbsp minced cilantro, leaves and stems",
      "1 large yellow onion, coarsely chopped",
      "1 1/2 tsp garam masala",
      "1 inch piece fresh ginger, (peeled and minced)",
      "2 cups mango chunks, (2 large mangoes) (fresh or frozen)",
    ];

    function processTryText(str: string) {
      state.ingredient = str;
      processIngredient();
    }

    async function processIngredient() {
      state.loading = true;
      const { data } = await api.recipes.parseIngredient(state.ingredient);

      if (data) {
        state.results = true;

        // TODO: Remove ts-ignore
        // ts-ignore because data will likely change significantly once I figure out how to return results
        // for the parser. For now we'll leave it like this
        // @ts-ignore
        properties.comments.value = data.ingredient.note || null;
        // @ts-ignore
        properties.quantity.value = data.ingredient.quantity || null;
        // @ts-ignore
        properties.unit.value = data.ingredient.unit.name || null;
        // @ts-ignore
        properties.food.value = data.ingredient.food.name || null;
      }
      state.loading = false;
    }

    const properties = reactive({
      quantity: {
        subtitle: "Quantity",
        value: "Value",
      },
      unit: {
        subtitle: "Unit",
        value: "Value",
      },
      food: {
        subtitle: "Food",
        value: "Value",
      },
      comments: {
        subtitle: "Comments",
        value: "Value",
      },
    });

    return {
      ...toRefs(state),
      tryText,
      properties,
      processTryText,
      processIngredient,
    };
  },
  head() {
    return {
      title: "Parser",
    };
  },
});
</script>
    
<style scoped>
</style>