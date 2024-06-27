<template>
  <v-container class="pa-0">
    <v-container>
      <BaseCardSectionTitle :title="$t('admin.ingredients-natural-language-processor')">
        {{ $t('admin.ingredients-natural-language-processor-explanation') }}

        <p class="pt-3">
          {{ $t('admin.ingredients-natural-language-processor-explanation-2') }}
        </p>
      </BaseCardSectionTitle>

      <div class="d-flex align-center justify-center justify-md-start flex-wrap">
        <v-btn-toggle v-model="parser" dense mandatory @change="processIngredient">
          <v-btn value="nlp"> {{ $t('admin.nlp') }} </v-btn>
          <v-btn value="brute"> {{ $t('admin.brute') }} </v-btn>
          <v-btn value="openai"> {{ $t('admin.openai') }} </v-btn>
        </v-btn-toggle>

        <v-checkbox v-model="showConfidence" class="ml-5" :label="$t('admin.show-individual-confidence')"></v-checkbox>
      </div>

      <v-card flat>
        <v-card-text>
          <v-text-field v-model="ingredient" :label="$t('admin.ingredient-text')"> </v-text-field>
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
          {{ $t('admin.average-confident', [getConfidence("average")]) }}
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
              {{ $t('admin.average-confident', [prop.confidence]) }}
            </v-chip>
          </div>
        </template>
      </div>
    </v-container>
    <v-container class="narrow-container">
      <v-card-title> {{ $t('admin.try-an-example') }} </v-card-title>
      <v-card v-for="(text, idx) in tryText" :key="idx" class="my-2" hover @click="processTryText(text)">
        <v-card-text> {{ text }} </v-card-text>
      </v-card>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, useContext } from "@nuxtjs/composition-api";
import { alert } from "~/composables/use-toast";
import { useUserApi } from "~/composables/api";
import { IngredientConfidence } from "~/lib/api/types/recipe";
import { Parser } from "~/lib/api/user/recipes/recipe";

type ConfidenceAttribute = "average" | "comment" | "name" | "unit" | "quantity" | "food";

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

    const { i18n } = useContext();

    const confidence = ref<IngredientConfidence>({});

    function getColor(attribute: ConfidenceAttribute) {
      const percentage = getConfidence(attribute);
      if (percentage === undefined) return;

      const p_as_num = parseFloat(percentage.replace("%", ""));

      // Set color based off range
      if (p_as_num > 75) {
        return "success";
      } else if (p_as_num > 60) {
        return "warning";
      } else {
        return "error";
      }
    }

    function getConfidence(attribute: ConfidenceAttribute) {
      if (!confidence.value) {
        return;
      }

      const property = confidence.value[attribute];
      if (property !== undefined) {
        return `${(property * 100).toFixed(0)}%`;
      }
      return undefined;
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

        if (data.confidence) confidence.value = data.confidence;

        // TODO: Remove ts-ignore
        // ts-ignore because data will likely change significantly once I figure out how to return results
        // for the parser. For now we'll leave it like this
        properties.comment.value = data.ingredient.note || "";
        properties.quantity.value = data.ingredient.quantity || "";
        properties.unit.value = data.ingredient?.unit?.name || "";
        properties.food.value = data.ingredient?.food?.name || "";

        (["comment", "quantity", "unit", "food"] as ConfidenceAttribute[]).forEach((property) => {
          const color = getColor(property);
          const confidence = getConfidence(property);
          if (color) {
            // @ts-ignore See above
            properties[property].color = color;
          }
          if (confidence) {
            // @ts-ignore See above
            properties[property].confidence = confidence;
          }
        });
      } else {
        alert.error(i18n.t("events.something-went-wrong") as string);
        state.results = false;
      }
      state.loading = false;
    }

    const properties = reactive({
      quantity: {
        subtitle: i18n.t("recipe.quantity"),
        value: "" as string | number,
        color: null,
        confidence: null,
      },
      unit: {
        subtitle: i18n.t("recipe.unit"),
        value: "",
        color: null,
        confidence: null,
      },
      food: {
        subtitle: i18n.t("shopping-list.food"),
        value: "",
        color: null,
        confidence: null,
      },
      comment: {
        subtitle: i18n.t("recipe.comment"),
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
      title: this.$t("admin.parser"),
    };
  },
});
</script>

<style scoped></style>
