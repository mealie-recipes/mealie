<template>
  <v-container>
    <v-menu
      v-model="state.picker"
      :close-on-content-click="false"
      transition="scale-transition"
      offset-y
      max-width="290px"
      min-width="auto"
    >
      <template #activator="{ on, attrs }">
        <v-btn color="primary" class="mb-2" v-bind="attrs" v-on="on">
          <v-icon left>
            {{ $globals.icons.calendar }}
          </v-icon>
          {{ $d(weekRange.start, "short") }} - {{ $d(weekRange.end, "short") }}
        </v-btn>
      </template>
      <v-date-picker
        v-model="state.range"
        no-title
        range
        :first-day-of-week="firstDayOfWeek"
        :local="$i18n.locale"
      >
        <v-text-field
          v-model="numberOfDays"
          type="number"
          :label="$t('meal-plan.numberOfDays-label')"
          :hint="$t('meal-plan.numberOfDays-hint')"
          persistent-hint
        />
        <v-spacer></v-spacer>
        <v-btn text color="primary" @click="state.picker = false">
          {{ $t("general.ok") }}
        </v-btn>
      </v-date-picker>
    </v-menu>

    <div class="d-flex flex-wrap align-center justify-space-between mb-2">
      <v-tabs style="width: fit-content;">
        <v-tab :to="`/household/mealplan/planner/view`">{{ $t('meal-plan.meal-planner') }}</v-tab>
        <v-tab :to="`/household/mealplan/planner/edit`">{{ $t('general.edit') }}</v-tab>
      </v-tabs>
      <ButtonLink :icon="$globals.icons.calendar" :to="`/household/mealplan/settings`" :text="$tc('general.settings')" />
    </div>

    <div>
      <NuxtChild :mealplans="mealsByDate" :actions="actions" />
    </div>

    <v-row> </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useRoute, useRouter, watch } from "@nuxtjs/composition-api";
import { isSameDay, addDays, parseISO } from "date-fns";
import { useHouseholdSelf } from "~/composables/use-households";
import { useMealplans } from "~/composables/use-group-mealplan";
import { useUserMealPlanPreferences } from "~/composables/use-users/preferences";

export default defineComponent({
  middleware: ["auth"],
  setup() {
    const route = useRoute();
    const router = useRouter();
    const { household } = useHouseholdSelf();

    const mealPlanPreferences = useUserMealPlanPreferences();
    const numberOfDays = ref<number>(mealPlanPreferences.value.numberOfDays || 7);
    watch(numberOfDays, (val) => {
      mealPlanPreferences.value.numberOfDays = Number(val);
    });

    // Force to /view if current route is /planner
    if (route.value.path === "/household/mealplan/planner") {
      router.push("/household/mealplan/planner/view");
    }

    function fmtYYYYMMDD(date: Date) {
      return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
    }

    function parseYYYYMMDD(date: string) {
      const [year, month, day] = date.split("-");
      return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    }

    const state = ref({
      range: [fmtYYYYMMDD(new Date()), fmtYYYYMMDD(addDays(new Date(), adjustForToday(numberOfDays.value)))] as [string, string],
      start: new Date(),
      picker: false,
      end: addDays(new Date(), adjustForToday(numberOfDays.value)),
    });

    const firstDayOfWeek = computed(() => {
      return household.value?.preferences?.firstDayOfWeek || 0;
    });

    const weekRange = computed(() => {
      const sorted = state.value.range.sort((a, b) => {
        return parseYYYYMMDD(a).getTime() - parseYYYYMMDD(b).getTime();
      });

      if (sorted.length === 2) {
        return {
          start: parseYYYYMMDD(sorted[0]),
          end: parseYYYYMMDD(sorted[1]),
        };
      }
      return {
        start: new Date(),
        end: addDays(new Date(), adjustForToday(numberOfDays.value)),
      };
    });

    const { mealplans, actions } = useMealplans(weekRange);

    function filterMealByDate(date: Date) {
      if (!mealplans.value) return [];
      return mealplans.value.filter((meal) => {
        const mealDate = parseISO(meal.date);
        return isSameDay(mealDate, date);
      });
    }

    function adjustForToday(days: number) {
      // The use case for this function is "how many days are we adding to 'today'?"
      // e.g. If the user wants 7 days, we substract one to do "today + 6"
      return days > 0 ? days - 1 : days + 1
    }

    const days = computed(() => {
      const numDays =
        Math.floor((weekRange.value.end.getTime() - weekRange.value.start.getTime()) / (1000 * 60 * 60 * 24)) + 1;

      // Calculate absolute value
      if (numDays < 0) return [];

      return Array.from(Array(numDays).keys()).map(
        (i) => {
          const date = new Date(weekRange.value.start.getTime());
          date.setDate(date.getDate() + i);
          return date;
        }
      );
    });

    const mealsByDate = computed(() => {
      return days.value.map((day) => {
        return { date: day, meals: filterMealByDate(day) };
      });
    });

    return {
      state,
      actions,
      mealsByDate,
      weekRange,
      firstDayOfWeek,
      numberOfDays,
    };
  },
  head() {
    return {
      title: this.$t("meal-plan.dinner-this-week") as string,
    };
  },
});
</script>

<style lang="css">
.left-color-border {
  border-left: 5px solid var(--v-primary-base) !important;
}

.bottom-color-border {
  border-bottom: 2px solid var(--v-primary-base) !important;
}
</style>
