<template>
  <BaseDialog
    v-model="dialog"
    :title="$t('edamam.dialog-title')"
    :icon="$globals.icons.foods"
    width="650"
  >
    <v-card-text>
      <!-- Search bar -->
      <div class="d-flex gap-2 mb-4">
        <v-text-field
          v-model="query"
          :label="$t('edamam.search-label')"
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
          {{ $t('edamam.search') }}
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
          {{ $t('edamam.select-result') }}
        </p>
        <v-list density="compact" rounded="lg" border>
          <v-list-item
            v-for="result in results"
            :key="result.foodId"
            :title="result.label"
            :subtitle="result.brand || result.category || ''"
            class="py-2"
            @click="selectResult(result)"
          >
            <template #append>
              <v-icon size="small" color="primary">
                {{ $globals.icons.chevronRight }}
              </v-icon>
            </template>
          </v-list-item>
        </v-list>
      </template>

      <!-- Nutrition preview after selection -->
      <template v-if="selectedResult">
        <div class="d-flex align-center mb-3">
          <v-btn
            icon
            variant="text"
            size="small"
            class="mr-1"
            @click="selectedResult = null"
          >
            <v-icon>{{ $globals.icons.backArrow }}</v-icon>
          </v-btn>
          <span class="text-subtitle-2">{{ selectedResult.label }}</span>
          <span v-if="selectedResult.brand" class="text-caption text-medium-emphasis ml-2">
            {{ selectedResult.brand }}
          </span>
        </div>

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
          {{ $t('edamam.source-note') }}
        </p>
      </template>
    </v-card-text>

    <template #custom-card-action>
      <BaseButton
        v-if="selectedResult"
        color="primary"
        @click="applyNutrition"
      >
        {{ $t('edamam.apply') }}
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useUserApi } from "~/composables/api";
import type { EdamamFoodResult } from "~/lib/api/types/recipe";

const dialog = defineModel<boolean>({ required: true });

const props = defineProps<{
  foodName?: string;
}>();

const emit = defineEmits<{
  apply: [data: EdamamFoodResult];
}>();

const i18n = useI18n();
const api = useUserApi();

const query = ref("");
const searching = ref(false);
const results = ref<EdamamFoodResult[]>([]);
const selectedResult = ref<EdamamFoodResult | null>(null);
const searchError = ref<string | null>(null);

// Pre-fill query with food name when dialog opens
watch(dialog, (open) => {
  if (open) {
    query.value = props.foodName || "";
    results.value = [];
    selectedResult.value = null;
    searchError.value = null;
  }
});

async function search() {
  if (!query.value.trim()) return;
  searching.value = true;
  searchError.value = null;
  results.value = [];
  selectedResult.value = null;

  const { data, error } = await api.foods.edamamSearch(query.value.trim());
  searching.value = false;

  if (error) {
    const detail = (error as any)?.response?.data?.detail;
    if (detail && detail.includes("EDAMAM_APP_ID")) {
      searchError.value = i18n.t("edamam.not-configured");
    } else {
      searchError.value = detail
        ? `${i18n.t("edamam.search-failed")}: ${detail}`
        : i18n.t("edamam.search-failed");
    }
    return;
  }
  if (!data || data.length === 0) {
    searchError.value = i18n.t("edamam.no-results");
    return;
  }
  results.value = data;
}

function selectResult(result: EdamamFoodResult) {
  selectedResult.value = result;
}

const nutritionRows = computed(() => {
  if (!selectedResult.value) return [];
  const d = selectedResult.value;
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

function applyNutrition() {
  if (selectedResult.value) {
    emit("apply", selectedResult.value);
    dialog.value = false;
  }
}
</script>
