<template>
  <section
    v-if="!loading"
    class="recommendations-section"
  >
    <template v-if="recommendations.length">
      <div class="d-flex flex-column flex-md-row align-md-center justify-space-between ga-3 mb-4">
        <div>
          <div class="text-h6 font-weight-medium">
            Recommended for You
          </div>
          <div class="text-body-2 text-medium-emphasis">
            Suggestions update as you rate and dismiss recipes.
          </div>
        </div>
        <v-chip
          v-if="coldStart"
          color="primary"
          variant="tonal"
          size="small"
        >
          Rate recipes to personalize this list
        </v-chip>
      </div>

      <div class="recommendation-strip">
        <v-card
          v-for="recipe in recommendations"
          :key="recipe.recipeId"
          class="recommendation-card"
          variant="outlined"
        >
          <div class="recommendation-image">
            <v-img
              v-if="recipe.recipeId"
              :src="staticRoutes.recipeSmallImage(recipe.recipeId, recipe.image || '', imageKey)"
              cover
              height="160"
            />
            <div
              v-else
              class="recommendation-placeholder"
            >
              <v-icon size="40">
                mdi-silverware-fork-knife
              </v-icon>
            </div>
          </div>

          <v-card-text class="pb-3">
            <div class="text-subtitle-1 font-weight-medium recommendation-title">
              {{ recipe.name }}
            </div>
            <p class="text-body-2 text-medium-emphasis recommendation-description">
              {{ recipe.description || "Fresh picks from your recipe library." }}
            </p>

            <div
              v-if="recipe.becauseTags?.length"
              class="d-flex flex-wrap ga-1 mt-3"
            >
              <v-chip
                v-for="tag in recipe.becauseTags.slice(0, 3)"
                :key="`${recipe.recipeId}-${tag}`"
                size="x-small"
                variant="outlined"
              >
                {{ tag }}
              </v-chip>
            </div>

            <div
              v-if="recipe.score !== null && recipe.score !== undefined"
              class="text-caption text-medium-emphasis mt-3"
            >
              Match score {{ recipe.score.toFixed(2) }}
            </div>
          </v-card-text>

          <v-card-actions class="px-4 pb-4 pt-0">
            <v-btn
              color="primary"
              variant="text"
              @click="openRecipe(recipe.slug)"
            >
              View
            </v-btn>
            <v-spacer />
            <v-btn
              variant="text"
              color="default"
              @click="dismissRecipe(recipe.recipeId)"
            >
              Dismiss
            </v-btn>
          </v-card-actions>
        </v-card>
      </div>
    </template>

    <v-card
      v-else
      class="recommendation-empty"
      variant="outlined"
    >
      <v-card-text class="pa-6 pa-md-8">
        <div class="text-h6 font-weight-medium mb-2">
          Recommendations will appear after you add recipes
        </div>
        <p class="text-body-2 text-medium-emphasis mb-0">
          Your taste profile was saved, but this household does not have any recipes in its library yet. Add or import a few recipes first, then Mealie can rank them for you.
        </p>
      </v-card-text>
    </v-card>
  </section>
</template>

<script setup lang="ts">
import type { RecommendationItem } from "~/lib/api/types/recommendations";
import { useUserApi } from "~/composables/api";
import { useStaticRoutes } from "~/composables/api/static-routes";

const auth = useMealieAuth();
const api = useUserApi();
const route = useRoute();
const staticRoutes = useStaticRoutes();

const recommendations = ref<RecommendationItem[]>([]);
const coldStart = ref(false);
const loading = ref(true);
const imageKey = ref(Date.now());

async function loadRecommendations() {
  if (!auth.user.value) {
    loading.value = false;
    return;
  }

  try {
    const status = await api.recommendations.getStatus();
    if (status.data?.needsOnboarding) {
      await navigateTo("/preferences");
      return;
    }

    const response = await api.recommendations.getRecommendations();
    recommendations.value = response.data?.recommendations ?? [];
    coldStart.value = response.data?.coldStart ?? false;
  }
  finally {
    loading.value = false;
  }
}

function openRecipe(slug?: string | null) {
  const routeGroupSlug = typeof route.params.groupSlug === "string" ? route.params.groupSlug : null;
  const groupSlug = routeGroupSlug || auth.user.value?.groupSlug;
  if (!groupSlug || !slug) {
    return;
  }
  navigateTo(`/g/${groupSlug}/r/${slug}`);
}

async function dismissRecipe(recipeId: string) {
  recommendations.value = recommendations.value.filter(recipe => recipe.recipeId !== recipeId);
  await api.recommendations.dismiss({ recipeId });
}

onMounted(loadRecommendations);
</script>

<style scoped>
.recommendations-section {
  margin-top: 0.75rem;
}

.recommendation-empty {
  border-style: dashed;
}

.recommendation-strip {
  display: grid;
  gap: 1rem;
  grid-auto-columns: minmax(260px, 320px);
  grid-auto-flow: column;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  scroll-snap-type: x proximity;
}

.recommendation-card {
  scroll-snap-align: start;
}

.recommendation-image {
  min-height: 160px;
  background: linear-gradient(135deg, rgba(32, 52, 84, 0.12), rgba(54, 122, 98, 0.16));
}

.recommendation-placeholder {
  align-items: center;
  color: rgba(0, 0, 0, 0.45);
  display: flex;
  height: 160px;
  justify-content: center;
}

.recommendation-title {
  line-height: 1.35;
}

.recommendation-description {
  display: -webkit-box;
  margin-top: 0.5rem;
  min-height: 3.25rem;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
</style>
