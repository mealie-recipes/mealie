<template>
  <v-tooltip
    location="bottom"
    nudge-right="50"
    :color="buttonStyle ? 'info' : 'secondary'"
  >
    <template #activator="{ props: tooltipProps }">
      <v-btn
        v-if="isInMealPlan || showAlways"
        icon
        :variant="buttonStyle ? 'flat' : undefined"
        :rounded="buttonStyle ? 'circle' : undefined"
        size="small"
        :color="buttonStyle ? 'info' : 'secondary'"
        :fab="buttonStyle"
        v-bind="{ ...tooltipProps, ...$attrs }"
        @click.prevent="handleClick"
      >
        <v-icon
          :size="!buttonStyle ? undefined : 'x-large'"
          :color="buttonStyle ? 'white' : 'secondary'"
        >
          {{ isInMealPlan ? $globals.icons.calendarCheck : $globals.icons.calendarBlank }}
        </v-icon>
      </v-btn>
    </template>
    <span>{{ tooltipText }}</span>
  </v-tooltip>

  <!-- Confirmation Dialog for Dated Entries -->
  <BaseDialog
    v-model="confirmDialog"
    :title="$t('recipe.scheduled-mealplan-entries')"
    :icon="$globals.icons.alertCircle"
    color="error"
    can-confirm
    @confirm="removeAllEntries"
  >
    <v-card-text>
      <p class="mb-4">
        {{ $t("recipe.confirm-remove-scheduled-entries") }}
      </p>
      <v-list>
        <v-list-item
          v-for="plan in sortedDatedPlans"
          :key="plan.id"
        >
          <v-list-item-title>
            {{ formatDateWithDay(plan.date) }}
            <span v-if="plan.entryType"> - {{ $t(`meal-plan.${plan.entryType}`) }}</span>
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-card-text>
  </BaseDialog>
</template>

<script setup lang="ts">
import { useRecipeMealPlans } from "~/composables/use-recipe-mealplans";
import { alert } from "~/composables/use-toast";

interface Props {
  recipeId?: string;
  showAlways?: boolean;
  buttonStyle?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  recipeId: "",
  showAlways: false,
  buttonStyle: false,
});

const i18n = useI18n();
const { getMealPlansForRecipe, addToMealPlanWithoutDate, removeMealPlanEntries } = useRecipeMealPlans();

const confirmDialog = ref(false);

const mealPlans = computed(() => getMealPlansForRecipe(props.recipeId));
const isInMealPlan = computed(() => mealPlans.value.length > 0);

const datedPlans = computed(() => mealPlans.value.filter(plan => plan.date !== null && plan.date !== undefined));
const unassignedPlans = computed(() => mealPlans.value.filter(plan => plan.date === null || plan.date === undefined));

// Sort dated plans by date (earliest first), then by entry type
const sortedDatedPlans = computed(() => {
  const entryTypeOrder = ["breakfast", "lunch", "dinner", "side", "snack", "drink", "dessert"];

  return [...datedPlans.value].sort((a, b) => {
    // First sort by date (earliest first)
    const dateA = a.date ? new Date(a.date).getTime() : 0;
    const dateB = b.date ? new Date(b.date).getTime() : 0;
    if (dateA !== dateB) {
      return dateA - dateB;
    }

    // Then sort by entry type
    const typeA = a.entryType || "";
    const typeB = b.entryType || "";
    return entryTypeOrder.indexOf(typeA) - entryTypeOrder.indexOf(typeB);
  });
});

const tooltipText = computed(() => {
  if (!isInMealPlan.value) {
    return i18n.t("recipe.add-to-plan");
  }

  // Only unassigned entries
  if (datedPlans.value.length === 0) {
    return i18n.t("recipe.in-mealplan-without-date");
  }

  // Has dated entries
  const firstDate = formatDateWithDay(sortedDatedPlans.value[0].date);

  if (sortedDatedPlans.value.length === 1) {
    return i18n.t("recipe.in-mealplan-with-date", { date: firstDate });
  }

  // Multiple dated entries
  const additionalCount = sortedDatedPlans.value.length - 1;
  return i18n.t("recipe.in-mealplan-with-date-and-more", { date: firstDate, count: additionalCount });
});

function formatDateWithDay(dateString: string | null | undefined): string {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString(i18n.locale.value, {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

async function handleClick() {
  if (!isInMealPlan.value) {
    // Not in meal plan - add it without date
    const result = await addToMealPlanWithoutDate(props.recipeId);
    if (result.success) {
      alert.success(i18n.t("recipe.recipe-added-to-mealplan-unassigned") as string);
    }
    else {
      alert.error(i18n.t("recipe.failed-to-add-recipe-without-date") as string);
    }
  }
  else if (datedPlans.value.length === 0) {
    // Only unassigned entries - remove them directly
    const planIds = unassignedPlans.value.map(p => p.id);
    const result = await removeMealPlanEntries(planIds);
    if (result.success) {
      alert.success(i18n.t("recipe.recipe-removed-from-mealplan") as string);
    }
    else {
      alert.error(i18n.t("recipe.recipe-removed-from-mealplan-failed") as string);
    }
  }
  else {
    // Has dated entries - show confirmation dialog
    confirmDialog.value = true;
  }
}

async function removeAllEntries() {
  const planIds = mealPlans.value.map(p => p.id);
  const result = await removeMealPlanEntries(planIds);
  confirmDialog.value = false;

  if (result.success) {
    alert.success(i18n.t("recipe.recipe-removed-from-mealplan") as string);
  }
  else {
    alert.error(i18n.t("recipe.recipe-removed-from-mealplan-failed") as string);
  }
}
</script>
