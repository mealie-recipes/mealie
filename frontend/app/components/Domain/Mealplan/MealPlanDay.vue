<template>
  <RecipeDialogAddToShoppingList
    v-model="shoppingListDialog"
    :recipes="recipesWithScales"
    :shopping-lists="shoppingLists"
  />
  <GroupMealPlanEntryDialog
    v-model="dialog.open"
    :entry="dialog.entry"
    :date="dialog.date"
    @create="actions.createOne($event)"
    @update="actions.updateOne($event)"
  />
  <template v-if="inlineActions">
    <MealPlanDayHeader :day="day" />
    <slot />
    <!-- Day Column Actions -->
    <div class="d-flex justify-end">
      <BaseButtonGroup
        v-bind="bindings"
        :buttons="inlineButtons"
      />
    </div>
  </template>
  <template v-else>
    <MealPlanDayHeader :day="day">
      <BaseButtonGroup
        v-bind="bindings"
        :buttons="[{
          icon: $globals.icons.dotsVertical,
          event: '',
          text: '',
          children: [
            {
              text: $t('meal-plan.add-day-to-list'),
              icon: $globals.icons.cartCheck,
              event: 'shopping-list',
              loading: addAllLoading,
              disabled: !props.recipes.length,
            },
            ...commonButtons,
            ...randomButtons,
          ],
        }]"
      />
    </MealPlanDayHeader>
    <slot />
  </template>
</template>

<script setup lang="ts">
import { format } from "date-fns";
import { useUserApi } from "~/composables/api";
import { useAddToShoppingListDialog } from "~/composables/shopping-list-page/use-add-to-shopping-list-dialog";
import type { PlanEntryType, ReadPlanEntry } from "~/lib/api/types/meal-plan";
import type { Recipe } from "~/lib/api/types/recipe";

interface Props {
  recipes?: Recipe[];
  day: Date;
  actions: ReturnType<typeof useMealplans>["actions"];
  inlineActions?: boolean;
}

const { open: shoppingListDialog, shoppingLists, addAllLoading, addAllToList } = useAddToShoppingListDialog();
const { $globals } = useNuxtApp();
const i18n = useI18n();
const api = useUserApi();
const props = withDefaults(defineProps<Props>(), {
  recipes: () => [],
  meal: () => ({}),
});

const commonButtons = [
  {
    icon: $globals.icons.createAlt,
    text: i18n.t("general.new"),
    event: "create",
  },
  {
    icon: $globals.icons.potSteam,
    text: i18n.t("meal-plan.random-dinner"),
    event: "randomDinner",
  },
  {
    icon: $globals.icons.bowlMixOutline,
    text: i18n.t("meal-plan.random-side"),
    event: "randomSide",
    divider: true,
  },
];
const randomButtons = [
  {
    icon: $globals.icons.diceMultiple,
    text: i18n.t("meal-plan.breakfast"),
    event: "randomBreakfast",
  },
  {
    icon: $globals.icons.diceMultiple,
    text: i18n.t("meal-plan.lunch"),
    event: "randomLunch",
  },
  {
    icon: $globals.icons.diceMultiple,
    text: i18n.t("meal-plan.side"),
    event: "randomSide",
  },
  {
    icon: $globals.icons.diceMultiple,
    text: i18n.t("meal-plan.snack"),
    event: "randomSnack",
  },
  {
    icon: $globals.icons.diceMultiple,
    text: i18n.t("meal-plan.drink"),
    event: "randomDrink",
  },
  {
    icon: $globals.icons.diceMultiple,
    text: i18n.t("meal-plan.dessert"),
    event: "randomDessert",
  },
];
const inlineButtons = [
  {
    icon: $globals.icons.diceMultiple,
    text: i18n.t("meal-plan.random-meal"),
    event: "random",
    children: randomButtons,
  },
  ...commonButtons,
];

const recipesWithScales = computed(() => {
  return props.recipes.map(recipe => ({ scale: 1, ...recipe }));
});

async function randomMeal(date: Date, type: PlanEntryType) {
  const { data } = await api.mealplans.setRandom({
    date: format(date, "yyyy-MM-dd"),
    entryType: type,
  });

  if (data) {
    props.actions.refreshAll();
  }
}

const dialog = reactive({
  open: false,
  entry: null as ReadPlanEntry | null,
  date: null as Date | null,
});

function openDialog() {
  dialog.entry = null;
  dialog.date = props.day;
  dialog.open = true;
}

const bindings = {
  onCreate: openDialog,
  onRandomBreakfast: () => randomMeal(props.day, "breakfast"),
  onRandomLunch: () => randomMeal(props.day, "lunch"),
  onRandomDinner: () => randomMeal(props.day, "dinner"),
  onRandomSide: () => randomMeal(props.day, "side"),
  onRandomSnack: () => randomMeal(props.day, "snack"),
  onRandomDrink: () => randomMeal(props.day, "drink"),
  onRandomDessert: () => randomMeal(props.day, "dessert"),
  onShoppingList: addAllToList,
};
</script>
