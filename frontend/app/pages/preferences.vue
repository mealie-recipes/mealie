<template>
  <v-container class="preference-page py-10">
    <v-row justify="center">
      <v-col
        cols="12"
        md="10"
        lg="8"
      >
        <v-card
          class="preference-shell"
          rounded="xl"
        >
          <div class="preference-hero">
            <div>
              <div class="text-overline mb-3">
                Personalized Recipe Recommendations
              </div>
              <h1 class="text-h3 font-weight-bold mb-4">
                Tell Mealie what you like to cook
              </h1>
              <p class="text-body-1 preference-copy">
                Pick at least two tags to seed your taste profile. You can keep refining it later just by rating
                recipes in your library.
              </p>
            </div>
          </div>

          <v-card-text class="pa-6 pa-md-8">
            <div class="tag-grid">
              <button
                v-for="tag in tags"
                :key="tag.id"
                type="button"
                class="tag-card"
                :class="{ 'tag-card--active': selected.includes(tag.id) }"
                @click="toggle(tag.id)"
              >
                <span class="text-subtitle-1 font-weight-medium">{{ tag.label }}</span>
                <span class="text-body-2 text-medium-emphasis">{{ tag.caption }}</span>
              </button>
            </div>

            <div class="d-flex flex-column flex-md-row align-md-center justify-space-between ga-4 mt-8">
              <div class="text-body-2 text-medium-emphasis">
                {{ selected.length }} selected
              </div>
              <div class="d-flex ga-3">
                <v-btn
                  variant="text"
                  :disabled="saving || selected.length === 0"
                  @click="selected = []"
                >
                  Clear
                </v-btn>
                <v-btn
                  color="primary"
                  size="large"
                  :disabled="selected.length < 2"
                  :loading="saving"
                  @click="savePreferences"
                >
                  Get My Recommendations
                </v-btn>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";

definePageMeta({
  layout: "blank",
});

const auth = useMealieAuth();
const api = useUserApi();

const selected = ref<string[]>([]);
const saving = ref(false);

const tags = [
  { id: "italian", label: "Italian", caption: "Pasta nights and classic comfort dishes" },
  { id: "asian", label: "Asian", caption: "Noodles, stir-fries, and bold aromatics" },
  { id: "mexican", label: "Mexican", caption: "Tacos, salsas, and rich spice blends" },
  { id: "indian", label: "Indian", caption: "Curries, dals, and layered spice" },
  { id: "vegetarian", label: "Vegetarian", caption: "Vegetable-forward everyday meals" },
  { id: "vegan", label: "Vegan", caption: "Plant-based mains and sides" },
  { id: "healthy", label: "Healthy", caption: "Lighter meals with fresh ingredients" },
  { id: "comfort-food", label: "Comfort Food", caption: "Warm, hearty, familiar favorites" },
  { id: "desserts", label: "Desserts", caption: "Cookies, cakes, and sweet endings" },
  { id: "baking", label: "Baking", caption: "Bread, pastries, and oven projects" },
  { id: "30-minutes-or-less", label: "Under 30 Minutes", caption: "Fast weeknight cooking" },
  { id: "high-protein", label: "High Protein", caption: "Meals built for staying power" },
];

function toggle(id: string) {
  selected.value = selected.value.includes(id)
    ? selected.value.filter(tag => tag !== id)
    : [...selected.value, id];
}

async function savePreferences() {
  if (selected.value.length < 2 || saving.value) {
    return;
  }

  saving.value = true;
  try {
    await api.recommendations.setPreferences({ tags: selected.value });
    const groupSlug = auth.user.value?.groupSlug;
    await navigateTo(groupSlug ? `/g/${groupSlug}` : "/");
  }
  finally {
    saving.value = false;
  }
}

onMounted(async () => {
  if (!auth.user.value) {
    await navigateTo("/login");
    return;
  }

  const status = await api.recommendations.getStatus();
  if (!status.data?.needsOnboarding) {
    const groupSlug = auth.user.value.groupSlug;
    await navigateTo(groupSlug ? `/g/${groupSlug}` : "/");
  }
});
</script>

<style scoped>
.preference-page {
  background:
    radial-gradient(circle at top left, rgba(40, 110, 90, 0.18), transparent 28%),
    radial-gradient(circle at top right, rgba(190, 121, 55, 0.16), transparent 24%),
    linear-gradient(180deg, #f7f4eb 0%, #ffffff 100%);
  min-height: 100vh;
}

.preference-shell {
  border: 1px solid rgba(22, 34, 51, 0.08);
  overflow: hidden;
}

.preference-hero {
  background: linear-gradient(135deg, #18314f 0%, #215f4f 100%);
  color: white;
  padding: 3rem 2rem;
}

.preference-copy {
  max-width: 42rem;
  opacity: 0.9;
}

.tag-grid {
  display: grid;
  gap: 0.9rem;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.tag-card {
  background: #fff;
  border: 1px solid rgba(24, 49, 79, 0.14);
  border-radius: 1rem;
  color: #18314f;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  min-height: 132px;
  padding: 1rem;
  text-align: left;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease,
    transform 0.15s ease;
}

.tag-card:hover {
  border-color: rgba(24, 49, 79, 0.34);
  box-shadow: 0 10px 24px rgba(24, 49, 79, 0.08);
  transform: translateY(-1px);
}

.tag-card span:first-child {
  color: #18314f;
}

.tag-card span:last-child {
  color: rgba(24, 49, 79, 0.72);
}

.tag-card--active {
  background: linear-gradient(180deg, #f1f9f5 0%, #ffffff 100%);
  border-color: #2a7a61;
  box-shadow: 0 0 0 2px rgba(42, 122, 97, 0.14);
}
</style>
