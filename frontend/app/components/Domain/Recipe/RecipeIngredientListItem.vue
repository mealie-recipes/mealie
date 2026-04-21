<template>
  <div>
    <div class="text-subtitle-1 dense-markdown ingredient-item">
      <SafeMarkdown
        v-if="parsedIng.quantity"
        class="d-inline"
        :source="parsedIng.quantity"
      />
      <template v-if="parsedIng.unit">
        {{ parsedIng.unit }}
      </template>
      <SafeMarkdown
        v-if="parsedIng.note && !parsedIng.name"
        class="text-bold d-inline"
        :source="parsedIng.note"
      />
      <template v-else-if="parsedIng.recipeLink">
        <SafeMarkdown v-if="parsedIng.recipeLink" class="text-bold d-inline" :source="parsedIng.recipeLink" />
        <SafeMarkdown v-if="parsedIng.note" class="note" :source="parsedIng.note" />
      </template>
      <template v-else>
        <SafeMarkdown
          v-if="parsedIng.name"
          class="text-bold d-inline"
          :source="parsedIng.name"
        />
        <SafeMarkdown
          v-if="parsedIng.note"
          class="note"
          :source="parsedIng.note"
        />
      </template>
    </div>

    <div v-if="canSuggestSubstitutions" class="substitution-panel" @click.stop>
      <v-btn
        size="x-small"
        variant="text"
        color="primary"
        :loading="isLoading"
        @click.stop="loadSuggestions"
      >
        Suggest Substitute
      </v-btn>
      <div v-if="errorMessage" class="text-caption text-error mt-1">
        {{ errorMessage }}
      </div>
      <div v-if="substitutions.length" class="mt-1">
        <div
          v-for="substitution in substitutions"
          :key="`${substitution.rank}-${substitution.ingredient}`"
          class="text-caption substitution-item"
        >
          <span>{{ substitution.rank }}. {{ substitution.ingredient }}</span>
          <span class="text-medium-emphasis">({{ substitution.embeddingScore.toFixed(2) }})</span>
          <v-btn
            size="x-small"
            variant="text"
            color="success"
            :loading="feedbackState[substitution.ingredient]?.loading"
            @click.stop="sendFeedback(substitution.ingredient, true)"
          >
            Accept
          </v-btn>
          <v-btn
            size="x-small"
            variant="text"
            color="warning"
            :loading="feedbackState[substitution.ingredient]?.loading"
            @click.stop="sendFeedback(substitution.ingredient, false)"
          >
            Reject
          </v-btn>
          <span v-if="feedbackState[substitution.ingredient]?.done" class="text-medium-emphasis">
            {{ feedbackState[substitution.ingredient]?.message }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RecipeIngredient } from "~/lib/api/types/household";
import type { SubstitutionPredictResponse, SubstitutionPrediction } from "~/lib/api/types/non-generated";
import { useUserApi } from "~/composables/api";
import { useIngredientTextParser } from "~/composables/recipes";

interface Props {
  ingredient: RecipeIngredient;
  scale?: number;
  recipeSlug?: string;
  enableSubstitutions?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  scale: 1,
  recipeSlug: "",
  enableSubstitutions: false,
});
const route = useRoute();
const auth = useMealieAuth();
const groupSlug = computed(() => route.params.groupSlug || auth.user?.value?.groupSlug || "");
const { useParsedIngredientText } = useIngredientTextParser();
const api = useUserApi();

const parsedIng = computed(() => {
  return useParsedIngredientText(props.ingredient, props.scale, true, groupSlug.value.toString());
});

const predictResponse = ref<SubstitutionPredictResponse | null>(null);
const substitutions = computed<SubstitutionPrediction[]>(() => predictResponse.value?.substitutions || []);
const isLoading = ref(false);
const errorMessage = ref("");
const feedbackState = ref<Record<string, { loading: boolean; done: boolean; message: string }>>({});

const canSuggestSubstitutions = computed(() => {
  return props.enableSubstitutions && !!props.recipeSlug && !!props.ingredient.referenceId;
});

async function loadSuggestions() {
  if (!canSuggestSubstitutions.value) {
    return;
  }

  isLoading.value = true;
  errorMessage.value = "";

  const { data, error } = await api.recipes.getIngredientSubstitutions(
    props.recipeSlug,
    props.ingredient.referenceId || "",
  );

  if (error || !data) {
    errorMessage.value = "Unable to load substitutions.";
  }
  else {
    predictResponse.value = data;
  }

  isLoading.value = false;
}

async function sendFeedback(substitution: string, userAccepted: boolean) {
  if (!predictResponse.value?.requestId || !canSuggestSubstitutions.value) {
    return;
  }

  feedbackState.value[substitution] = { loading: true, done: false, message: "" };

  const { error } = await api.recipes.sendIngredientSubstitutionFeedback(
    props.recipeSlug,
    props.ingredient.referenceId || "",
    {
      requestId: predictResponse.value.requestId,
      suggestedSubstitution: substitution,
      userAccepted,
      modelVersion: predictResponse.value.modelVersion,
    },
  );

  feedbackState.value[substitution] = {
    loading: false,
    done: !error,
    message: error ? "Feedback failed." : "Feedback sent.",
  };
}
</script>

<style lang="scss">
.ingredient-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25em;
  word-break: break-word;
  min-width: 0;

  .d-inline {
    & > p {
      display: inline;
      &:has(> sub) > sup {
        letter-spacing: -0.05rem;
      }
    }
    &:has(sub) {
      &:after {
        letter-spacing: -0.2rem;
      }
    }
    sup {
      & + span {
        letter-spacing: -0.05rem;
      }
      &:before {
        letter-spacing: 0rem;
      }
    }
  }

  .text-bold {
    font-weight: bold;
    white-space: normal;
    word-break: break-word;
  }
}

.note {
  flex-basis: 100%;
  width: 100%;
  display: block;
  line-height: 1.3em;
  font-size: 0.8em;
  opacity: 0.7;
  white-space: normal;
  word-break: break-word;
}

.substitution-panel {
  margin-top: 0.25rem;
}

.substitution-item {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  align-items: center;
}
</style>
