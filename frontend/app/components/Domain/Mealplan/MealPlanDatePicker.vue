<template>
  <v-date-picker
    v-model="selectedDate"
    class="mx-auto"
    hide-header
    show-adjacent-months
    color="primary"
    :first-day-of-week="firstDayOfWeek"
    :local="$i18n.locale"
    :events="hasMealPlanned"
    @update:month="updateMonth"
    @update:year="updateYear"
  >
    <template #controls="{ yearText, monthYearText, prevMonth, nextMonth, disabled }">
      <div class="d-flex justify-space-between w-100">
        <v-btn :disabled="disabled.includes('prev-month')" :icon="$globals.icons.chevronLeft" flat density="comfortable" @click="prevMonth" />
        <div class="text-center">
          <div class="text-body-large">
            {{ monthYearText.split(' ')[0] }}
          </div>
          <div class="text-body-small">
            {{ yearText }}
          </div>
        </div>
        <v-btn :disabled="disabled.includes('next-month')" :icon="$globals.icons.chevronRight" flat density="comfortable" @click="nextMonth" />
      </div>
    </template>
  </v-date-picker>
</template>

<script setup lang="ts">
import { addMonths, format, isDate } from "date-fns";
import type { DatePickerEventColorValue } from "vuetify/lib/components/VDatePicker/VDatePickerMonth.mjs";
import type { PlanEntryType } from "~/lib/api/types/meal-plan";

const selectedDate = defineModel<Date | [Date, Date]>();
const props = defineProps<{
  entryType?: PlanEntryType;
}>();

const { household } = useHouseholdSelf();

const target = ref(new Date());
const range = computed(() => ({
  start: addMonths(target.value, -1),
  end: addMonths(target.value, 2),
}));
const { mealplans } = useMealplans(range);

const firstDayOfWeek = computed(() => {
  return household.value?.preferences?.firstDayOfWeek || 0;
});

function updateMonth(month: number) {
  const copy = new Date(target.value);
  copy.setMonth(month);
  target.value = copy;
}

function updateYear(year: number) {
  const copy = new Date(target.value);
  copy.setFullYear(year);
  target.value = copy;
}

function hasMealPlanned(date: string): DatePickerEventColorValue {
  const planned = mealplans.value ?? [];
  const dateMatched = planned.filter(meal => meal.date === date);
  const typeMatched = dateMatched.filter(meal => !props.entryType || meal.entryType === props.entryType);
  const earlierDate = isDate(selectedDate.value) ? selectedDate.value : selectedDate.value?.[0];
  const laterDate = isDate(selectedDate.value) ? selectedDate.value : selectedDate.value?.[1];
  const isSelected = (earlierDate && date === format(earlierDate, "yyyy-MM-dd")) || (laterDate && date === format(laterDate, "yyyy-MM-dd"));
  if (!dateMatched.length) return false;
  if (typeMatched.length) return isSelected ? "primary-lighten-3" : "primary";
  return isSelected ? "grey-lighten-3" : "grey";
}
</script>
