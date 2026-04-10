<template>
  <BaseDialog
    v-model="dialog"
    :title="$t('usda.dialog-title')"
    :icon="$globals.icons.foods"
    width="650"
  >
    <v-card-text>
      <!-- Search bar -->
      <div class="d-flex gap-2 mb-4">
        <v-text-field
          v-model="query"
          :label="$t('usda.search-label')"
          :placeholder="foodName"
          hide-details
          variant="outlined"
          density="compact"
          class="flex-grow-1"
          @keyup.enter="search"
        />
        <v-btn
          color="primary"
          :loading="searching"
          :disabled="!query.trim()"
          @click="search"
        >
          {{ $t('usda.search') }}
        </v-btn>
      </div>

      <!-- Error banner -->
      <v-alert
        v-if="searchError"
        type="error"
        class="mb-3"
        density="compact"
      >
        {{ searchError }}
      </v-alert>

      <!-- Results list -->
      <template v-if="results.length > 0 && !selectedResult">
        <p class="text-caption text-medium-emphasis mb-2">
          {{ $t('usda.select-result') }}
        </p>
        <v-list density="compact" rounded="lg" border>
          <v-list-item
            v-for="result in results"
            :key="result.fdcId"
            :title="result.description"
            :subtitle="result.brandOwner || `FDC ID: ${result.fdcId}`"
            class="py-2"
            @click="selectResult(result)"
          >
            <template #append>
              <v-chip
                v-if="result.confidence != null"
                size="x-small"
                :color="confidenceColor(result.confidence)"
                class="mr-2"
              >
                {{ Math.round(result.confidence * 100) }}%
              </v-chip>
              <v-icon size="small" color="primary">
                {{ $globals.icons.chevronRight }}
              </v-icon>
            </template>
          </v-list-item>
        </v-list>
      </template>

      <!-- Nutrition preview after selection -->
      <template v-if="selectedResult && nutritionData">
        <div class="d-flex align-center mb-3">
          <v-btn
            icon
            variant="text"
            size="small"
            class="mr-1"
            @click="selectedResult = null; nutritionData = null"
          >
            <v-icon>{{ $globals.icons.backArrow }}</v-icon>
          </v-btn>
          <span class="text-subtitle-2">{{ selectedResult.description }}</span>
        </div>

        <v-alert
          v-if="fetchError"
          type="error"
          density="compact"
          class="mb-3"
        >
          {{ fetchError }}
        </v-alert>

        <v-table density="compact" class="rounded-lg border">
          <thead>
            <tr>
              <th>{{ $t('usda.nutrient') }}</th>
              <th class="text-right">{{ $t('usda.per-100g') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in nutritionRows" :key="row.label">
              <td>{{ row.label }}</td>
              <td class="text-right">{{ row.value != null ? `${row.value} ${row.unit}` : '—' }}</td>
            </tr>
          </tbody>
        </v-table>

        <p class="text-caption text-medium-emphasis mt-3">
          {{ $t('usda.source-note') }}
        </p>
      </template>

      <!-- Loading nutrition -->
      <div v-if="fetchingNutrition" class="d-flex justify-center py-6">
        <v-progress-circular indeterminate color="primary" />
      </div>
    </v-card-text>

    <template #custom-card-action>
      <BaseButton
        v-if="nutritionData && !fetchError"
        color="primary"
        @click="applyNutrition"
      >
        {{ $t('usda.apply') }}
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useUserApi } from "~/composables/api";
import type { UsdaFoodResult, UsdaNutritionData } from "~/lib/api/types/recipe";

const dialog = defineModel<boolean>({ required: true });

const props = defineProps<{
  foodName?: string;
}>();

const emit = defineEmits<{
  apply: [data: UsdaNutritionData, meta: { fdcId: number; description: string; confidence: number | null }];
}>();

const i18n = useI18n();
const api = useUserApi();

const query = ref("");
const searching = ref(false);
const fetchingNutrition = ref(false);
const results = ref<UsdaFoodResult[]>([]);
const selectedResult = ref<UsdaFoodResult | null>(null);
const nutritionData = ref<UsdaNutritionData | null>(null);
const searchError = ref<string | null>(null);
const fetchError = ref<string | null>(null);

// Pre-fill query with food name when dialog opens
watch(dialog, (open) => {
  if (open) {
    query.value = props.foodName || "";
    results.value = [];
    selectedResult.value = null;
    nutritionData.value = null;
    searchError.value = null;
    fetchError.value = null;
  }
});

async function search() {
  if (!query.value.trim()) return;
  searching.value = true;
  searchError.value = null;
  results.value = [];
  selectedResult.value = null;
  nutritionData.value = null;

  const { data, error } = await api.foods.usdaSearch(query.value.trim());
  searching.value = false;

  if (error) {
    const detail = (error as any)?.response?.data?.detail;
    searchError.value = detail
      ? `${i18n.t("usda.search-failed")}: ${detail}`
      : i18n.t("usda.search-failed");
    return;
  }
  if (!data || data.length === 0) {
    searchError.value = i18n.t("usda.no-results");
    return;
  }
  results.value = data;
}

async function selectResult(result: UsdaFoodResult) {
  selectedResult.value = result;
  fetchingNutrition.value = true;
  fetchError.value = null;
  nutritionData.value = null;

  const { data, error } = await api.foods.usdaFetchNutrition(result.fdcId);
  fetchingNutrition.value = false;

  if (error || !data) {
    fetchError.value = i18n.t("usda.fetch-failed");
    return;
  }
  nutritionData.value = data;
}

const nutritionRows = computed(() => {
  if (!nutritionData.value) return [];
  const d = nutritionData.value;
  return [
    { label: i18n.t("recipe.calories"), value: d.calories, unit: "kcal" },
    { label: i18n.t("recipe.protein-content"), value: d.proteinContent, unit: "g" },
    { label: i18n.t("recipe.fat-content"), value: d.fatContent, unit: "g" },
    { label: i18n.t("recipe.carbohydrate-content"), value: d.carbohydrateContent, unit: "g" },
    { label: i18n.t("recipe.fiber-content"), value: d.fiberContent, unit: "g" },
    { label: i18n.t("recipe.sugar-content"), value: d.sugarContent, unit: "g" },
    { label: i18n.t("recipe.saturated-fat-content"), value: d.saturatedFatContent, unit: "g" },
    { label: i18n.t("recipe.unsaturated-fat-content"), value: d.unsaturatedFatContent, unit: "g" },
    { label: i18n.t("recipe.trans-fat-content"), value: d.transFatContent, unit: "g" },
    { label: i18n.t("recipe.sodium-content"), value: d.sodiumContent, unit: "mg" },
    { label: i18n.t("recipe.cholesterol-content"), value: d.cholesterolContent, unit: "mg" },
  ].map(r => ({ ...r, value: r.value != null ? Math.round(r.value * 10) / 10 : null }));
});

function confidenceColor(score: number): string {
  if (score >= 0.75) return "success";
  if (score >= 0.50) return "warning";
  return "error";
}

function applyNutrition() {
  if (nutritionData.value && selectedResult.value) {
    emit("apply", nutritionData.value, {
      fdcId: selectedResult.value.fdcId,
      description: selectedResult.value.description,
      confidence: selectedResult.value.confidence ?? null,
    });
    dialog.value = false;
  }
}
</script>
