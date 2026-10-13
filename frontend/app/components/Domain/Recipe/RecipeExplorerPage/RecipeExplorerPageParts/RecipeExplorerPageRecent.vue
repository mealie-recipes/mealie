<template>
  <section v-if="loading || recipes.length" class="recent">
    <div class="recent__header">
      <h2 class="recent__title">
        {{ $t("recipe-library.recently-added") }}
      </h2>
      <button type="button" class="recent__link" @click="$emit('see-all')">
        {{ $t("recipe-library.see-all") }}
      </button>
    </div>
    <div class="recent__grid">
      <template v-if="loading">
        <div v-for="n in RECENT_COUNT" :key="n" class="recent-card">
          <div class="recent-card__photo mealie-photo-placeholder" />
        </div>
      </template>
      <RouterLink
        v-for="recipe in recipes"
        v-else
        :key="recipe.id!"
        :to="`/g/${groupSlug}/r/${recipe.slug}`"
        class="recent-card"
      >
        <div class="recent-card__photo mealie-photo-placeholder">
          <img
            v-if="recipe.image && !failedImages[recipe.id!]"
            :src="recipeSmallImage(recipe.id!, recipe.image)"
            alt=""
            loading="lazy"
            @error="failedImages[recipe.id!] = true"
          >
        </div>
        <div class="recent-card__text">
          <div class="recent-card__name">
            {{ recipe.name }}
          </div>
          <div v-if="meta(recipe)" class="recent-card__meta">
            {{ meta(recipe) }}
          </div>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useStaticRoutes, usePublicExploreApi, useUserApi } from "~/composables/api";
import { useRecipeTime } from "~/composables/recipes";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import type { RecipeSummary } from "~/lib/api/types/recipe";

defineEmits<{
  "see-all": [];
}>();

const RECENT_COUNT = 4;

const auth = useMealieAuth();
const route = useRoute();
const { isOwnGroup } = useLoggedInState();
const { recipeSmallImage } = useStaticRoutes();
const { recipeShortTime } = useRecipeTime();

const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

const loading = ref(true);
const recipes = ref<RecipeSummary[]>([]);
const failedImages = reactive<Record<string, boolean>>({});

onMounted(async () => {
  const params = { orderBy: "created_at", orderDirection: "desc" };
  const { data } = isOwnGroup.value
    ? await useUserApi().recipes.getAll(1, RECENT_COUNT, params)
    : await usePublicExploreApi(groupSlug.value).explore.recipes.getAll(1, RECENT_COUNT, params);
  recipes.value = data?.items ?? [];
  loading.value = false;
});

function meta(recipe: RecipeSummary) {
  return [recipeShortTime(recipe), recipe.recipeCategory?.[0]?.name].filter(Boolean).join(" · ");
}
</script>

<style scoped>
.recent__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  white-space: nowrap;
}

.recent__title {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--mealie-ink);
}

.recent__link {
  border: 0;
  background: none;
  padding: 0;
  font: inherit;
  font-size: 15px;
  color: rgb(var(--v-theme-primary));
  cursor: pointer;
}

.recent__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  margin-top: 14px;
}

.recent-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: var(--mealie-ink);
  text-decoration: none;
}

.recent-card__photo {
  position: relative;
  height: 180px;
  border-radius: 18px;
  overflow: hidden;
}

.recent-card__photo img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.recent-card:hover .recent-card__photo img {
  transform: scale(1.03);
}

.recent-card__text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.recent-card__name {
  font-size: 15px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-card__meta {
  font-size: 13px;
  color: var(--mealie-text-tertiary);
}

@media (max-width: 960px) {
  .recent__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
