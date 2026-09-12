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
      <MealPlanDatePicker v-model="newMealdate" :entry-type="newMealType" />
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
import { alert } from "~/composables/use-toast";
import type { PlanEntryType } from "~/lib/api/types/meal-plan";

const props = defineProps<{
  recipeId: string;
}>();

const mealplannerDialog = defineModel<boolean>({
  default: false,
});

const i18n = useI18n();
const api = useUserApi();
const planTypeOptions = usePlanTypeOptions();
const router = useRouter();

const newMealType = ref<PlanEntryType>("dinner");
const newMealdate = ref(new Date());

const newMealdateString = computed(() => {
  // Format the date to YYYY-MM-DD in the same timezone as newMealdate
  const year = newMealdate.value.getFullYear();
  const month = String(newMealdate.value.getMonth() + 1).padStart(2, "0");
  const day = String(newMealdate.value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
});

async function addRecipeToPlan() {
  const { response } = await api.mealplans.createOne({
    date: newMealdateString.value,
    entryType: newMealType.value,
    title: "",
    text: "",
    recipeId: props.recipeId,
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
