<template>
  <BaseDialog
    v-model="dialog"
    :icon="$globals.icons.units"
    :title="$t('unit.convert-unit')"
    :loading="loading"
    width="500"
    @cancel="dialog = false"
  >
    <v-card-text>
      <v-row>
        <!-- From quantity -->
        <v-col cols="4">
          <v-number-input
            v-model="fromQuantity"
            :label="$t('recipe.quantity')"
            density="compact"
            variant="outlined"
            control-variant="stacked"
            inset
            :precision="null"
            :min="0"
            hide-details
          />
        </v-col>

        <!-- From unit -->
        <v-col cols="8">
          <v-autocomplete
            v-model="fromUnit"
            :items="allUnitsWithStd"
            :label="$t('unit.from-unit')"
            item-title="name"
            return-object
            density="compact"
            variant="outlined"
            hide-details
            clearable
            @update:model-value="toUnit = null; result = null"
          />
        </v-col>
      </v-row>

      <!-- Arrow -->
      <div class="d-flex justify-center align-center my-3">
        <v-icon size="x-large" color="primary">
          {{ $globals.icons.arrowDown }}
        </v-icon>
      </div>

      <!-- To unit -->
      <v-autocomplete
        v-model="toUnit"
        :items="compatibleUnits"
        :label="$t('unit.to-unit')"
        item-title="name"
        return-object
        density="compact"
        variant="outlined"
        hide-details
        clearable
        :disabled="!fromUnit"
        @update:model-value="convertNow"
      />

      <!-- Result -->
      <v-alert
        v-if="result !== null"
        class="mt-4"
        type="success"
        variant="tonal"
      >
        <span class="text-h6">{{ formattedResult }}</span>
      </v-alert>
      <v-alert
        v-if="errorMsg"
        class="mt-4"
        type="error"
        variant="tonal"
      >
        {{ errorMsg }}
      </v-alert>

      <!-- Convert button -->
      <div class="d-flex justify-end mt-3 gap-2">
        <v-btn
          variant="tonal"
          :loading="loading"
          :disabled="!fromUnit || !toUnit"
          @click="convertNow"
        >
          {{ $t('unit.convert') }}
        </v-btn>
        <v-btn
          v-if="result !== null && toUnit && applyable"
          color="primary"
          variant="flat"
          @click="applyConversion"
        >
          {{ $t('unit.apply') }}
        </v-btn>
      </div>
    </v-card-text>
  </BaseDialog>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { useUnitStore } from "~/composables/store";
import type { IngredientUnit, RecipeIngredient } from "~/lib/api/types/recipe";

/** Standard unit strings that belong to the volume dimension */
const VOLUME_STANDARDS = new Set(["fluid_ounce", "cup", "milliliter", "liter"]);
/** Standard unit strings that belong to the weight dimension */
const WEIGHT_STANDARDS = new Set(["ounce", "pound", "gram", "kilogram"]);

interface Props {
  /** When provided, the dialog is pre-filled and an "Apply" button appears to update the ingredient. */
  ingredient?: RecipeIngredient | null;
}

const props = withDefaults(defineProps<Props>(), {
  ingredient: null,
});

const emit = defineEmits<{
  /** Emitted when the user clicks "Apply". Parent should update the ingredient. */
  apply: [quantity: number, unit: IngredientUnit];
}>();

const dialog = defineModel<boolean>({ default: false });

const api = useUserApi();
const unitStore = useUnitStore();
const { $globals } = useNuxtApp();
const i18n = useI18n();

const loading = ref(false);
const errorMsg = ref<string | null>(null);
const result = ref<number | null>(null);

const fromQuantity = ref<number>(1);
const fromUnit = ref<IngredientUnit | null>(null);
const toUnit = ref<IngredientUnit | null>(null);

/** True when the dialog was opened from an ingredient editor (has a pre-filled unit). */
const applyable = computed(() => !!props.ingredient);

/** All units that have standardization data (can participate in conversion). */
const allUnitsWithStd = computed(() =>
  (unitStore.store.value as IngredientUnit[]).filter(u => u.standardQuantity && u.standardUnit),
);

function dimensionOf(unit: IngredientUnit | null): "volume" | "weight" | null {
  if (!unit?.standardUnit) return null;
  if (VOLUME_STANDARDS.has(unit.standardUnit)) return "volume";
  if (WEIGHT_STANDARDS.has(unit.standardUnit)) return "weight";
  return null;
}

/** Units in the same dimension as fromUnit (excluding fromUnit itself). */
const compatibleUnits = computed(() => {
  const dim = dimensionOf(fromUnit.value);
  if (!dim) return allUnitsWithStd.value;
  return allUnitsWithStd.value.filter(u => dimensionOf(u) === dim && u.id !== fromUnit.value?.id);
});

/** Nicely formatted result string, e.g. "2.5 cups" */
const formattedResult = computed(() => {
  if (result.value === null || !toUnit.value) return "";
  const qty = Math.round(result.value * 1000) / 1000; // round to 3 dp
  const unitName = (qty === 1 ? toUnit.value.name : toUnit.value.pluralName) || toUnit.value.name;
  return `${qty} ${unitName}`;
});

async function convertNow() {
  if (!fromUnit.value || !toUnit.value) return;
  errorMsg.value = null;
  result.value = null;
  loading.value = true;

  try {
    const { data, error } = await api.units.convert({
      fromUnit: fromUnit.value.id,
      toUnit: toUnit.value.id,
      quantity: fromQuantity.value,
    });
    if (error) {
      errorMsg.value = error?.data?.detail || i18n.t("unit.conversion-failed");
    }
    else if (data) {
      result.value = data.toQuantity;
    }
  }
  finally {
    loading.value = false;
  }
}

function applyConversion() {
  if (result.value === null || !toUnit.value) return;
  emit("apply", result.value, toUnit.value);
  dialog.value = false;
}

// Pre-fill when ingredient prop changes or dialog opens
watch(dialog, (open) => {
  if (!open) return;
  errorMsg.value = null;
  result.value = null;
  toUnit.value = null;

  if (props.ingredient?.quantity) {
    fromQuantity.value = props.ingredient.quantity;
  }
  else {
    fromQuantity.value = 1;
  }

  if (props.ingredient?.unit && "id" in props.ingredient.unit) {
    fromUnit.value = props.ingredient.unit as IngredientUnit;
  }
  else {
    fromUnit.value = null;
  }
});
</script>
