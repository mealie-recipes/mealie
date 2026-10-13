<template>
  <div class="recipe-hero-wrap">
    <!-- Toolbar -->
    <div class="recipe-toolbar d-print-none">
      <RouterLink :to="`/g/${groupSlug}`" class="recipe-toolbar__back">
        <svg width="8" height="13" viewBox="0 0 12 20" aria-hidden="true"><polyline
          points="10,2 2,10 10,18"
          fill="none"
          stroke="currentColor"
          stroke-width="2.6"
          stroke-linecap="round"
          stroke-linejoin="round"
        /></svg>
        {{ $t("general.recipes") }}
      </RouterLink>
      <div class="recipe-toolbar__actions">
        <button
          v-if="isOwnGroup && canEditRecipe"
          type="button"
          class="mealie-pill mealie-pill--sm"
          @click="setMode(PageMode.EDIT)"
        >
          {{ $t("general.edit") }}
        </button>
        <button
          v-if="isOwnGroup"
          type="button"
          class="mealie-pill mealie-pill--sm"
          @click="runAction('share')"
        >
          {{ $t("general.share") }}
        </button>
        <RecipeTimelineBadge
          v-if="isOwnGroup"
          pill
          :slug="recipe.slug"
          :recipe-name="recipe.name!"
        />
        <button
          v-if="isOwnGroup"
          type="button"
          class="mealie-pill mealie-pill--sm mealie-pill--icon mealie-pill--tinted"
          :aria-pressed="isFavorite"
          :aria-label="isFavorite ? $t('recipe.remove-from-favorites') : $t('recipe.add-to-favorites')"
          :title="isFavorite ? $t('recipe.remove-from-favorites') : $t('recipe.add-to-favorites')"
          @click="toggleFavorite"
        >
          <v-icon size="16">
            {{ isFavorite ? $globals.icons.heart : $globals.icons.heartOutline }}
          </v-icon>
        </button>
        <v-menu location="bottom end" :offset="6" eager content-class="d-print-none">
          <template #activator="{ props: menuProps }">
            <button
              type="button"
              class="mealie-pill mealie-pill--sm mealie-pill--icon"
              :aria-label="$t('general.menu')"
              v-bind="menuProps"
            >
              <v-icon size="18">
                {{ $globals.icons.dotsHorizontal }}
              </v-icon>
            </button>
          </template>
          <RecipeContextMenuContent
            ref="actions"
            :name="recipe.name!"
            :slug="recipe.slug!"
            :recipe="recipe"
            :recipe-id="recipe.id!"
            :recipe-scale="scale"
            :use-items="{
              edit: false,
              download: isOwnGroup,
              duplicate: isOwnGroup,
              mealplanner: isOwnGroup,
              shoppingList: isOwnGroup,
              print: true,
              printPreferences: true,
              share: isOwnGroup,
              recipeActions: true,
              delete: isOwnGroup && canEditRecipe,
            }"
            @print="printRecipe"
          />
        </v-menu>
      </div>
    </div>

    <!-- Hero -->
    <div class="recipe-hero">
      <button
        type="button"
        class="recipe-hero__photo mealie-photo-placeholder"
        :class="{ 'recipe-hero__photo--zoom': showImage }"
        :disabled="!showImage"
        :aria-label="recipe.name || ''"
        @click="lightboxOpen = true"
      >
        <img
          v-if="showImage"
          :key="imageKey"
          :src="recipeImageUrl"
          alt=""
          @error="imageFailed = true"
        >
      </button>
      <RecipeImageLightbox
        v-if="lightboxOpen"
        v-model="lightboxOpen"
        :image-url="recipeFullImageUrl"
        :image-alt="recipe.name || ''"
      />

      <div class="recipe-hero__info">
        <div v-if="eyebrow" class="recipe-hero__eyebrow">
          {{ eyebrow }}
        </div>
        <h1 class="recipe-hero__title">
          {{ recipe.name }}
        </h1>
        <SafeMarkdown
          v-if="recipe.description"
          :source="recipe.description"
          class="recipe-hero__description"
        />

        <div v-if="stats.length || showRating" class="recipe-hero__stats">
          <div v-for="stat in stats" :key="stat.label" class="recipe-hero__stat">
            <span class="recipe-hero__stat-label">{{ stat.label }}</span>
            <span class="recipe-hero__stat-value">{{ stat.value }}</span>
          </div>
          <div v-if="showRating" class="recipe-hero__stat">
            <span class="recipe-hero__stat-label">{{ $t("general.rating") }}</span>
            <RecipeRating
              :key="recipe.slug"
              class="recipe-hero__rating"
              small
              :model-value="recipe.rating || 0"
              :recipe-id="recipe.id!"
              :slug="recipe.slug!"
            />
          </div>
        </div>

        <div class="recipe-hero__actions d-print-none">
          <button
            type="button"
            class="mealie-pill mealie-pill--lg mealie-pill--primary recipe-hero__cook"
            @click="setMode(PageMode.COOK)"
          >
            <svg width="10" height="12" viewBox="0 0 12 14" aria-hidden="true"><path d="M1 1 L11 7 L1 13 Z" fill="currentColor" /></svg>
            {{ $t("recipe-library.start-cooking") }}
          </button>
          <template v-if="isOwnGroup">
            <button type="button" class="mealie-pill mealie-pill--lg" @click="runAction('mealplanner')">
              {{ $t("recipe.add-to-plan") }}
            </button>
            <button type="button" class="mealie-pill mealie-pill--lg" @click="runAction('shoppingList')">
              {{ $t("recipe.add-to-list") }}
            </button>
          </template>
        </div>
        <RecipeLastMade
          v-if="isOwnGroup"
          :recipe="recipe"
          class="recipe-hero__last-made d-print-none"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import RecipeContextMenuContent from "~/components/Domain/Recipe/RecipeContextMenu/RecipeContextMenuContent.vue";
import RecipeImageLightbox from "~/components/Domain/Recipe/RecipeImageLightbox.vue";
import RecipeLastMade from "~/components/Domain/Recipe/RecipeLastMade.vue";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import RecipeTimelineBadge from "~/components/Domain/Recipe/RecipeTimelineBadge.vue";
import { useStaticRoutes, useUserApi } from "~/composables/api";
import { useRecipePermissions, useRecipeTime } from "~/composables/recipes";
import { PageMode, usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserSelfRatings } from "~/composables/use-users";
import type { HouseholdSummary } from "~/lib/api/types/household";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";

interface Props {
  recipe: NoUndefinedField<Recipe>;
  scale?: number;
}
const props = withDefaults(defineProps<Props>(), {
  scale: 1,
});

const i18n = useI18n();
const auth = useMealieAuth();
const route = useRoute();
const display = useDisplay();
const { isOwnGroup } = useLoggedInState();
const { user } = usePageUser();
const { imageKey, setMode } = usePageState(props.recipe.slug);
const { recipeImage, recipeSmallImage } = useStaticRoutes();
const { recipeShortTime } = useRecipeTime();

const groupSlug = computed(() => (route.params.groupSlug as string) || auth.user.value?.groupSlug || "");

/* ---------- Permissions ---------- */
const recipeHousehold = ref<HouseholdSummary>();
if (user.id) {
  useUserApi().households.getOne(props.recipe.householdId).then(({ data }) => {
    recipeHousehold.value = data || undefined;
  });
}
const { canEditRecipe } = useRecipePermissions(props.recipe, recipeHousehold, user);

/* ---------- Actions ---------- */
const actions = ref<InstanceType<typeof RecipeContextMenuContent> | null>(null);

function runAction(event: string) {
  actions.value?.runAction(event);
}

function printRecipe() {
  window.print();
}

const { userRatings, refreshUserRatings } = useUserSelfRatings();
const isFavorite = computed(() => !!userRatings.value.find(r => r.recipeId === props.recipe.id)?.isFavorite);

async function toggleFavorite() {
  const userId = auth.user.value?.id;
  if (!userId || !props.recipe.id) {
    return;
  }
  const api = useUserApi();
  if (isFavorite.value) {
    await api.users.removeFavorite(userId, props.recipe.id);
  }
  else {
    await api.users.addFavorite(userId, props.recipe.id);
  }
  await refreshUserRatings();
}

/* ---------- Image ---------- */
const imageFailed = ref(false);
const lightboxOpen = ref(false);
const showImage = computed(() => !!props.recipe.image && !imageFailed.value);
const recipeFullImageUrl = computed(() => recipeImage(props.recipe.id, props.recipe.image, imageKey.value));
const recipeImageUrl = computed(() =>
  display.smAndDown.value
    ? recipeSmallImage(props.recipe.id, props.recipe.image, imageKey.value)
    : recipeFullImageUrl.value,
);
watch(recipeImageUrl, () => {
  imageFailed.value = false;
});

/* ---------- Details ---------- */
const eyebrow = computed(() =>
  [...(props.recipe.recipeCategory || []), ...(props.recipe.tags || [])]
    .slice(0, 3)
    .map(item => item.name)
    .join(" · "),
);

const servings = computed(() => {
  const base = props.recipe.recipeServings || props.recipe.recipeYieldQuantity;
  if (!base) {
    return props.recipe.recipeYield || "";
  }
  return String(Math.round(base * props.scale * 100) / 100);
});

const stats = computed(() => {
  const short = (seconds: number | null | undefined, text: string | null | undefined) =>
    recipeShortTime({ totalTimeSeconds: seconds, totalTime: text });

  const prep = short(props.recipe.prepTimeSeconds, props.recipe.prepTime);
  const cook = short(props.recipe.performTimeSeconds, props.recipe.performTime);
  const total = short(props.recipe.totalTimeSeconds, props.recipe.totalTime);

  return [
    { label: i18n.t("recipe-page.prep"), value: prep },
    { label: i18n.t("recipe-page.cook"), value: cook },
    // the total only adds something when prep and cook don't already tell the whole story
    { label: i18n.t("recipe-page.total"), value: prep && cook ? "" : total },
    { label: i18n.t("recipe-page.serves"), value: servings.value },
  ].filter(stat => stat.value);
});

const showRating = computed(() => isOwnGroup.value || !!props.recipe.rating);
</script>

<style scoped>
.recipe-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 56px;
  padding: 0 32px;
  border-bottom: 1px solid var(--mealie-hairline);
  white-space: nowrap;
}

.recipe-toolbar__back {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgb(var(--v-theme-primary));
  text-decoration: none;
}

.recipe-toolbar__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recipe-hero {
  display: grid;
  grid-template-columns: minmax(0, 560px) minmax(0, 1fr);
  gap: 44px;
  align-items: center;
  padding: 32px 48px 0;
}

.recipe-hero__photo {
  position: relative;
  height: 330px;
  padding: 0;
  border: 0;
  border-radius: 24px;
  overflow: hidden;
  cursor: default;
}

.recipe-hero__photo--zoom {
  cursor: zoom-in;
}

.recipe-hero__photo img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recipe-hero__info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.recipe-hero__eyebrow {
  font-size: 13px;
  font-weight: 600;
  color: rgb(var(--v-theme-primary));
}

.recipe-hero__title {
  margin-top: 8px;
  font-size: 44px;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.05;
  color: var(--mealie-ink);
  text-wrap: balance;
}

.recipe-hero__description {
  margin-top: 12px;
  max-width: 440px;
  font-size: 17px;
  line-height: 1.45;
  color: var(--mealie-text-secondary);
  text-wrap: pretty;
}

.recipe-hero__stats {
  display: flex;
  flex-wrap: wrap;
  row-gap: 12px;
  margin-top: 22px;
}

.recipe-hero__stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 24px;
  border-left: 1px solid var(--mealie-hairline-strong);
}

.recipe-hero__stat:first-child {
  padding-left: 0;
  border-left: 0;
}

.recipe-hero__stat-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--mealie-text-tertiary);
}

.recipe-hero__stat-value {
  font-size: 17px;
  font-weight: 600;
  color: var(--mealie-ink);
}

.recipe-hero__rating {
  margin-left: -4px;
  min-height: 25px;
  display: flex;
  align-items: center;
}

.recipe-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;
}

.recipe-hero__cook {
  box-shadow: 0 8px 20px rgba(var(--v-theme-primary), 0.28);
}

.recipe-hero__last-made {
  margin-top: 16px;
  align-self: flex-start;
}

@media (max-width: 1100px) {
  .recipe-hero {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 32px;
  }

  .recipe-hero__title {
    font-size: 36px;
  }
}

@media (max-width: 800px) {
  .recipe-toolbar {
    padding: 0 16px;
  }

  .recipe-hero {
    grid-template-columns: minmax(0, 1fr);
    gap: 20px;
    padding: 16px 16px 0;
  }

  .recipe-hero__photo {
    height: 240px;
  }

  .recipe-hero__title {
    font-size: 30px;
  }

  .recipe-hero__stat {
    padding: 0 16px;
  }
}

@media print {
  .recipe-hero {
    display: none;
  }
}
</style>
