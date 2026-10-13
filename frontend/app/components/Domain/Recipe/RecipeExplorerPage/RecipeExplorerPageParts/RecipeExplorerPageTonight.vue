<template>
  <section class="tonight">
    <!-- Tonight's plan -->
    <div class="tonight-hero" :class="{ 'mealie-photo-placeholder': !heroImage }">
      <img
        v-if="heroImage"
        :src="heroImage"
        alt=""
        class="tonight-hero__image"
        @error="heroImageFailed = true"
      >
      <div class="tonight-hero__scrim" />
      <div class="tonight-hero__content">
        <div class="tonight-hero__text">
          <div class="tonight-hero__eyebrow">
            {{ $t("recipe-library.tonights-plan") }}
          </div>
          <template v-if="tonight">
            <RouterLink v-if="tonightLink" :to="tonightLink" class="tonight-hero__title">
              {{ tonightTitle }}
            </RouterLink>
            <div v-else class="tonight-hero__title">
              {{ tonightTitle }}
            </div>
            <div v-if="tonightMeta" class="tonight-hero__meta">
              {{ tonightMeta }}
            </div>
          </template>
          <div v-else class="tonight-hero__title">
            {{ $t("recipe-library.nothing-planned-tonight") }}
          </div>
        </div>
        <RouterLink
          v-if="tonightLink"
          :to="`${tonightLink}?cook=true`"
          class="mealie-pill mealie-pill--lg tonight-hero__action"
        >
          <svg width="10" height="12" viewBox="0 0 10 12" aria-hidden="true"><path d="M1 1 L9 6 L1 11 Z" fill="currentColor" /></svg>
          {{ $t("recipe-library.start-cooking") }}
        </RouterLink>
        <RouterLink
          v-else-if="!loading"
          :to="plannerLink"
          class="mealie-pill mealie-pill--lg tonight-hero__action"
        >
          {{ $t("recipe-library.plan-a-meal") }}
        </RouterLink>
      </div>
    </div>

    <!-- This Week -->
    <div class="week">
      <div class="week__header">
        <span class="week__title">{{ $t("recipe-library.this-week") }}</span>
        <RouterLink :to="plannerLink" class="week__link">
          {{ $t("meal-plan.meal-planner") }}
        </RouterLink>
      </div>
      <div class="week__days">
        <div v-for="day in days" :key="day.key" class="week__day">
          <span class="week__day-name" :class="{ 'week__day-name--today': day.isToday }">{{ day.label }}</span>
          <template v-if="day.meals.length">
            <RouterLink
              v-if="day.meals[0]!.link"
              :to="day.meals[0]!.link"
              class="week__meal"
            >
              {{ day.meals[0]!.title }}
            </RouterLink>
            <span v-else class="week__meal">{{ day.meals[0]!.title }}</span>
            <span v-if="day.meals.length > 1" class="week__more">+{{ day.meals.length - 1 }}</span>
          </template>
          <span v-else class="week__meal week__meal--empty">{{ $t("recipe-library.nothing-planned") }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { addDays, format, isSameDay } from "date-fns";
import { useStaticRoutes, useUserApi } from "~/composables/api";
import { useRecipeTime } from "~/composables/recipes";
import type { PlanEntryType, ReadPlanEntry } from "~/lib/api/types/meal-plan";

const DAYS_SHOWN = 5;
// the order meals are picked in when a day has several, dinner first since that's "tonight"
const ENTRY_PRIORITY: PlanEntryType[] = ["dinner", "lunch", "breakfast", "side", "dessert", "snack", "drink"];

const api = useUserApi();
const i18n = useI18n();
const auth = useMealieAuth();
const route = useRoute();
const { recipeImage } = useStaticRoutes();
const { recipeShortTime } = useRecipeTime();

const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const plannerLink = "/household/mealplan/planner/view";

const loading = ref(true);
const entries = ref<ReadPlanEntry[]>([]);
const start = new Date();

onMounted(async () => {
  const { data } = await api.mealplans.getAll(1, -1, {
    start_date: format(start, "yyyy-MM-dd"),
    end_date: format(addDays(start, DAYS_SHOWN - 1), "yyyy-MM-dd"),
  });
  entries.value = data?.items ?? [];
  loading.value = false;
});

function byPriority(a: ReadPlanEntry, b: ReadPlanEntry) {
  const rank = (entry: ReadPlanEntry) => {
    const index = ENTRY_PRIORITY.indexOf(entry.entryType ?? "dinner");
    return index === -1 ? ENTRY_PRIORITY.length : index;
  };
  return rank(a) - rank(b);
}

function entryTitle(entry: ReadPlanEntry) {
  return entry.recipe?.name || entry.title || "";
}

function entryLink(entry: ReadPlanEntry) {
  return entry.recipe?.slug ? `/g/${groupSlug.value}/r/${entry.recipe.slug}` : "";
}

/** plan entries are dated without a time, so parse them as local days rather than UTC midnight */
function entryDate(entry: ReadPlanEntry) {
  const [year, month, day] = entry.date.split("-").map(Number);
  return new Date(year!, month! - 1, day!);
}

const days = computed(() =>
  Array.from({ length: DAYS_SHOWN }, (_, offset) => {
    const date = addDays(start, offset);
    const meals = entries.value
      .filter(entry => isSameDay(entryDate(entry), date))
      .sort(byPriority)
      .map(entry => ({ title: entryTitle(entry), link: entryLink(entry), entry }))
      .filter(meal => meal.title);
    return {
      key: format(date, "yyyy-MM-dd"),
      label: new Intl.DateTimeFormat(i18n.locale.value, { weekday: "short" }).format(date).toUpperCase(),
      isToday: offset === 0,
      meals,
    };
  }),
);

/**
 * tonight's meal is the day's first meal in priority order (dinner first), the same one the
 * week list shows; a note without a recipe still shows, just without "Start Cooking"
 */
const tonight = computed(() => days.value[0]?.meals[0]);
const tonightTitle = computed(() => tonight.value?.title ?? "");
const tonightLink = computed(() => tonight.value?.link ?? "");

const tonightMeta = computed(() => {
  const recipe = tonight.value?.entry.recipe;
  if (!recipe) {
    return "";
  }
  const servings = recipe.recipeServings || recipe.recipeYieldQuantity;
  return [
    recipeShortTime(recipe),
    servings ? i18n.t("recipe.serves-amount", { amount: servings }) : "",
  ].filter(Boolean).join(" · ");
});

const heroImageFailed = ref(false);
const heroImage = computed(() => {
  const recipe = tonight.value?.entry.recipe;
  if (!recipe?.id || !recipe.image || heroImageFailed.value) {
    return "";
  }
  return recipeImage(recipe.id, recipe.image);
});
watch(() => tonight.value?.entry.recipe?.id, () => {
  heroImageFailed.value = false;
});
</script>

<style scoped>
.tonight {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
  gap: 20px;
}

.tonight-hero {
  position: relative;
  height: 280px;
  border-radius: 24px;
  overflow: hidden;
}

.tonight-hero__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tonight-hero__scrim {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(20, 16, 12, 0.72) 0%, rgba(20, 16, 12, 0) 60%);
}

.tonight-hero__content {
  position: absolute;
  left: 28px;
  right: 28px;
  bottom: 24px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.tonight-hero__text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  color: #fff;
}

.tonight-hero__eyebrow {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #ffd2bf;
}

.tonight-hero__title {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.1;
  color: #fff;
  text-decoration: none;
  text-wrap: balance;
}

.tonight-hero__meta {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.85);
}

.tonight-hero__action,
.tonight-hero__action:hover {
  height: 40px;
  padding: 0 20px;
  background: #fff;
  color: #1c1b19;
  font-weight: 600;
}

.tonight-hero__action svg {
  color: rgb(var(--v-theme-primary));
}

.week {
  display: flex;
  flex-direction: column;
  height: 280px;
  padding: 20px 22px;
  border-radius: 24px;
  background: var(--mealie-surface);
  box-shadow: inset 0 0 0 1px var(--mealie-hairline);
  box-sizing: border-box;
}

.week__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  white-space: nowrap;
}

.week__title {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--mealie-ink);
}

.week__link {
  font-size: 14px;
  color: rgb(var(--v-theme-primary));
  text-decoration: none;
}

.week__days {
  display: flex;
  flex-direction: column;
  margin-top: 8px;
}

.week__day {
  display: flex;
  align-items: center;
  gap: 14px;
  height: 42px;
  border-bottom: 1px solid var(--mealie-hairline);
  white-space: nowrap;
}

.week__day:last-child {
  border-bottom: 0;
}

.week__day-name {
  width: 34px;
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--mealie-text-tertiary);
}

.week__day-name--today {
  color: rgb(var(--v-theme-primary));
}

.week__meal {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
  font-weight: 500;
  color: var(--mealie-ink);
  text-decoration: none;
}

a.week__meal:hover {
  color: rgb(var(--v-theme-primary));
}

.week__meal--empty {
  font-weight: 400;
  color: var(--mealie-text-tertiary);
}

.week__more {
  font-size: 12px;
  color: var(--mealie-text-tertiary);
}

@media (max-width: 960px) {
  .tonight {
    grid-template-columns: minmax(0, 1fr);
  }

  .week {
    height: auto;
  }
}

@media (max-width: 600px) {
  .tonight-hero {
    height: 240px;
  }

  .tonight-hero__content {
    left: 20px;
    right: 20px;
    bottom: 20px;
    flex-direction: column;
    align-items: flex-start;
  }

  .tonight-hero__title {
    font-size: 26px;
  }
}
</style>
