<template>
  <BaseDialog
    v-model="mealplannerDialog"
    bottom-sheet
    :title="$t('recipe.add-recipe-to-mealplan')"
    color="primary"
    :icon="$globals.icons.calendar"
    can-confirm
    @confirm="addRecipeToPlan"
  >
    <v-card-text>
      <MealPlanDatePicker v-model="pickerModel" :multiple="pickerMultiple" :entry-type="newMealType" />
      <!-- the dates are part of the label, so they stay with the switch instead of floating above the next field -->
      <v-switch
        v-model="isWeekEntry"
        color="primary"
        hide-details
        class="mb-2"
      >
        <template #label>
          <div>
            <div>{{ $t("meal-plan.plan-for-the-whole-week") }}</div>
            <div v-if="isWeekEntry" class="text-caption text-medium-emphasis">
              {{ $d(weekRange.start, "short") }} - {{ $d(weekRange.end, "short") }}
            </div>
          </div>
        </template>
      </v-switch>
      <v-select
        v-model="newMealType"
        :return-object="false"
        :items="planTypeOptions"
        :label="$t('recipe.entry-type')"
        item-title="text"
        item-value="value"
      />
    </v-card-text>
  </BaseDialog>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { useMealPlanEntryDates } from "~/composables/use-group-mealplan";
import { alert } from "~/composables/use-toast";
import type { PlanEntryType } from "~/lib/api/types/meal-plan";

const props = withDefaults(defineProps<{
  recipeId: string;
  recipeScale?: number;
}>(), {
  recipeScale: 1,
});

const mealplannerDialog = defineModel<boolean>({
  default: false,
});

const i18n = useI18n();
const api = useUserApi();
const planTypeOptions = usePlanTypeOptions();
const router = useRouter();

const newMealType = ref<PlanEntryType>("dinner");
const { isWeekEntry, weekRange, entryDatesPayload, pickerModel, pickerMultiple } = useMealPlanEntryDates();

async function addRecipeToPlan() {
  const { response } = await api.mealplans.createOne({
    ...entryDatesPayload.value,
    entryType: newMealType.value,
    title: "",
    text: "",
    recipeId: props.recipeId,
    recipeScale: props.recipeScale,
  });

  if (response?.status === 201) {
    alert.success(i18n.t("recipe.recipe-added-to-mealplan"), null, {
      action: {
        message: i18n.t("general.view"),
        onClick: () => router.push("/household/mealplan/planner/view"),
      },
    });
  }
  else {
    alert.error(i18n.t("recipe.failed-to-add-recipe-to-mealplan"));
  }
}
</script>
