<template>
  <v-container class="pa-0">
    <v-container>
      <BaseCardSectionTitle title="Ingredients Natural Language Processor">
        Mealie uses Conditional Random Fields (CRFs) for parsing and processing ingredients. The model used for
        ingredients is based off a data set of over 100,000 ingredients from a dataset compiled by the New York Times.
        Note that as the model is trained in English only, you may have varied results when using the model in other
        languages. This page is a playground for testing the model.

        <p class="pt-3">
          It's not perfect, but it yields great results in general and is a good starting point for manually parsing
          ingredients into individual fields. Alternatively, you can also use the "Brute" processor that uses a pattern
          matching technique to identify ingredients.
        </p>
      </BaseCardSectionTitle>

      <div class="d-flex align-center justify-center justify-md-start flex-wrap">
        <v-btn-toggle v-model="parser" dense mandatory @change="processIngredient">
          <v-btn value="nlp"> NLP </v-btn>
          <v-btn value="brute"> Brute </v-btn>
        </v-btn-toggle>

        <v-checkbox v-model="showConfidence" class="ml-5" label="Show individual confidence"></v-checkbox>
      </div>

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
      <div v-if="parser !== 'brute' && getConfidence('average')" class="d-flex">
        <v-chip dark :color="getColor('average')" class="mx-auto mb-2">
          {{ getConfidence("average") }} Confident
        </v-chip>
      </div>
      <div class="d-flex justify-center flex-wrap" style="gap: 1.5rem">
        <template v-for="(prop, index) in properties">
          <div v-if="prop.value" :key="index" class="flex-grow-1">
            <v-card min-width="200px">
              <v-card-title> {{ prop.value }} </v-card-title>
              <v-card-text>
                {{ prop.subtitle }}
              </v-card-text>
            </v-card>
            <v-chip v-if="prop.confidence && showConfidence" dark :color="prop.color" class="mt-2">
              {{ prop.confidence }} Confident
            </v-chip>
          </div>
        </template>
      </div>
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
import { defineComponent, reactive, ref, toRefs } from "@nuxtjs/composition-api";
import { Confidence, Parser } from "~/api/class-interfaces/recipes";
import { useUserApi } from "~/composables/api";

export default defineComponent({
  layout: "admin",
  setup() {
    const api = useUserApi();

    const state = reactive({
      loading: false,
      ingredient: "",
      results: false,
      parser: "nlp" as Parser,
    });

    const confidence = ref<Confidence>({});

    function getColor(attribute: string) {
      const percentage = getConfidence(attribute);

      // @ts-ignore
      const p_as_num = parseFloat(percentage?.replace("%", ""));

      // Set color based off range
      if (p_as_num > 75) {
        return "success";
      } else if (p_as_num > 60) {
        return "warning";
      } else {
        return "error";
      }
    }

    function getConfidence(attribute: string) {
      attribute = attribute.toLowerCase();
      if (!confidence.value) {
        return;
      }

      // @ts-ignore
      const property: number = confidence.value[attribute];
      if (property) {
        return `${(property * 100).toFixed(0)}%`;
      }
      return null;
    }

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
      if (state.ingredient === "") {
        return;
      }

      state.loading = true;

      const { data } = await api.recipes.parseIngredient(state.parser, state.ingredient);

      if (data) {
        state.results = true;

        confidence.value = data.confidence;

        // TODO: Remove ts-ignore
        // ts-ignore because data will likely change significantly once I figure out how to return results
        // for the parser. For now we'll leave it like this
        properties.comment.value = data.ingredient.note || "";
        properties.quantity.value = data.ingredient.quantity || "";
        properties.unit.value = data.ingredient?.unit?.name || "";
        properties.food.value = data.ingredient?.food?.name || "";

        for (const property in properties) {
          const color = getColor(property);
          const confidence = getConfidence(property);
          if (color) {
            // @ts-ignore
            properties[property].color = color;
          }
          if (confidence) {
            // @ts-ignore
            properties[property].confidence = confidence;
          }
        }
      }
      state.loading = false;
    }

    const properties = reactive({
      quantity: {
        subtitle: "Quantity",
        value: "" as any,
        color: null,
        confidence: null,
      },
      unit: {
        subtitle: "Unit",
        value: "",
        color: null,
        confidence: null,
      },
      food: {
        subtitle: "Food",
        value: "",
        color: null,
        confidence: null,
      },
      comment: {
        subtitle: "Comment",
        value: "",
        color: null,
        confidence: null,
      },
    });

    const showConfidence = ref(false);

    return {
      showConfidence,
      getColor,
      confidence,
      getConfidence,
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