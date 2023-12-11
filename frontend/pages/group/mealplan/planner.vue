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
      <v-date-picker v-model="state.range" no-title range>
        <v-spacer></v-spacer>
        <v-btn text color="primary" @click="state.picker = false">
          {{ $t("general.ok") }}
        </v-btn>
      </v-date-picker>
    </v-menu>

    <div class="d-flex flex-wrap align-center justify-space-between mb-2">
      <v-tabs style="width: fit-content;">
        <v-tab :to="`/group/mealplan/planner/view`">{{ $t('meal-plan.meal-planner') }}</v-tab>
        <v-tab :to="`/group/mealplan/planner/edit`">{{ $t('general.edit') }}</v-tab>
      </v-tabs>
      <ButtonLink :icon="$globals.icons.calendar" :to="`/group/mealplan/settings`" :text="$tc('general.settings')" />
    </div>

    <div>
      <NuxtChild :mealplans="mealsByDate" :actions="actions" />
    </div>

    <v-row> </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useRoute, useRouter } from "@nuxtjs/composition-api";
import { isSameDay, addDays, parseISO } from "date-fns";
import { useMealplans } from "~/composables/use-group-mealplan";

export default defineComponent({
  setup() {
    const route = useRoute();
    const router = useRouter();

    // Force to /view if current route is /planner
    if (route.value.path === "/group/mealplan/planner") {
      router.push("/group/mealplan/planner/view");
    }

    function fmtYYYYMMDD(date: Date) {
      return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
    }

    function parseYYYYMMDD(date: string) {
      const [year, month, day] = date.split("-");
      return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    }

    const state = ref({
      range: [fmtYYYYMMDD(new Date()), fmtYYYYMMDD(addDays(new Date(), 6))] as [string, string],
      start: new Date(),
      picker: false,
      end: addDays(new Date(), 6),
    });

    const recipeSearchTerm = ref("");

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
        end: addDays(new Date(), 6),
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
      recipeSearchTerm,
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
