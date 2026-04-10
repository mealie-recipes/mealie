<template>
  <BaseDialog
    v-model="dialog"
    :title="$t('recipal.dialog-title')"
    :icon="$globals.icons.foods"
    width="650"
  >
    <v-card-text>
      <!-- Filter + pagination controls -->
      <div class="d-flex gap-2 mb-3 align-center">
        <v-text-field
          v-model="nameFilter"
          :label="$t('recipal.filter-label')"
          hide-details
          variant="outlined"
          density="compact"
          clearable
          class="flex-grow-1"
        />
        <v-btn
          variant="text"
          :disabled="page <= 1 || loading"
          icon
          @click="goToPage(page - 1)"
        >
          <v-icon>{{ $globals.icons.chevronLeft }}</v-icon>
        </v-btn>
        <span class="text-caption text-medium-emphasis text-no-wrap">{{ $t('recipal.page', { n: page }) }}</span>
        <v-btn
          variant="text"
          :disabled="!hasMore || loading"
          icon
          @click="goToPage(page + 1)"
        >
          <v-icon>{{ $globals.icons.chevronRight }}</v-icon>
        </v-btn>
      </div>

      <!-- Error -->
      <v-alert v-if="listError" type="error" density="compact" class="mb-3">
        {{ listError }}
      </v-alert>

      <!-- Loading -->
      <div v-if="loading" class="d-flex justify-center py-6">
        <v-progress-circular indeterminate color="primary" />
      </div>

      <!-- Ingredient list -->
      <template v-if="!loading && !selectedIngredient">
        <v-list v-if="filteredIngredients.length > 0" density="compact" rounded="lg" border>
          <v-list-item
            v-for="ingredient in filteredIngredients"
            :key="ingredient.ingredientId"
            :title="ingredient.name"
            :subtitle="ingredient.brand || `ID: ${ingredient.ingredientId}`"
            class="py-2"
            @click="selectIngredient(ingredient)"
          >
            <template #append>
              <v-chip v-if="ingredient.usdaVerified" size="x-small" color="success" class="mr-2">
                USDA
              </v-chip>
              <v-icon size="small" color="primary">{{ $globals.icons.chevronRight }}</v-icon>
            </template>
          </v-list-item>
        </v-list>
        <p v-else class="text-body-2 text-medium-emphasis text-center py-4">
          {{ $t('recipal.no-ingredients') }}
        </p>
      </template>

      <!-- Nutrition preview -->
      <template v-if="selectedIngredient && nutritionData">
        <div class="d-flex align-center mb-3">
          <v-btn icon variant="text" size="small" class="mr-1" @click="selectedIngredient = null; nutritionData = null">
            <v-icon>{{ $globals.icons.backArrow }}</v-icon>
          </v-btn>
          <span class="text-subtitle-2">{{ selectedIngredient.name }}</span>
          <span v-if="selectedIngredient.brand" class="text-caption text-medium-emphasis ml-2">
            — {{ selectedIngredient.brand }}
          </span>
        </div>

        <v-alert v-if="fetchError" type="error" density="compact" class="mb-3">
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
          {{ $t('recipal.source-note') }}
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
import type { RecipalIngredientResult, UsdaNutritionData } from "~/lib/api/types/recipe";

const dialog = defineModel<boolean>({ required: true });

const emit = defineEmits<{
  apply: [data: UsdaNutritionData, meta: { ingredientId: number; name: string }];
}>();

const i18n = useI18n();
const api = useUserApi();

const page = ref(1);
const hasMore = ref(false);
const loading = ref(false);
const fetchingNutrition = ref(false);
const ingredients = ref<RecipalIngredientResult[]>([]);
const selectedIngredient = ref<RecipalIngredientResult | null>(null);
const nutritionData = ref<UsdaNutritionData | null>(null);
const nameFilter = ref("");
const listError = ref<string | null>(null);
const fetchError = ref<string | null>(null);

const filteredIngredients = computed(() => {
  const q = nameFilter.value.trim().toLowerCase();
  if (!q) return ingredients.value;
  return ingredients.value.filter(i => i.name.toLowerCase().includes(q));
});

async function loadPage(p: number) {
  loading.value = true;
  listError.value = null;
  selectedIngredient.value = null;
  nutritionData.value = null;

  const { data, error } = await api.foods.recipalListIngredients(p, 20);
  loading.value = false;

  if (error || !data) {
    const detail = (error as any)?.response?.data?.detail;
    listError.value = detail
      ? `${i18n.t("recipal.list-failed")}: ${detail}`
      : i18n.t("recipal.list-failed");
    return;
  }

  ingredients.value = data;
  hasMore.value = data.length === 20;
  page.value = p;
}

function goToPage(p: number) {
  nameFilter.value = "";
  loadPage(p);
}

watch(dialog, (open) => {
  if (open) {
    page.value = 1;
    nameFilter.value = "";
    ingredients.value = [];
    selectedIngredient.value = null;
    nutritionData.value = null;
    listError.value = null;
    fetchError.value = null;
    hasMore.value = false;
    loadPage(1);
  }
});

async function selectIngredient(ingredient: RecipalIngredientResult) {
  selectedIngredient.value = ingredient;
  fetchingNutrition.value = true;
  fetchError.value = null;
  nutritionData.value = null;

  const { data, error } = await api.foods.recipalFetchNutrition(ingredient.ingredientId);
  fetchingNutrition.value = false;

  if (error || !data) {
    fetchError.value = i18n.t("recipal.fetch-failed");
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

function applyNutrition() {
  if (nutritionData.value && selectedIngredient.value) {
    emit("apply", nutritionData.value, {
      ingredientId: selectedIngredient.value.ingredientId,
      name: selectedIngredient.value.name,
    });
    dialog.value = false;
  }
}
</script>
