<template>
  <div class="d-print-none">
    <div
      v-if="versions.length === 0"
      class="text-center text-grey pa-4"
    >
      {{ $t("recipe.version-no-history") }}
    </div>
    <v-list
      v-else
      density="compact"
    >
      <template
        v-for="(version, idx) in versions"
        :key="version.id"
      >
        <v-list-item
          :class="{ 'bg-grey-lighten-4': expandedVersion === version.id }"
          @click="toggleVersion(version)"
        >
          <template #prepend>
            <v-avatar
              size="28"
              color="primary"
              class="mr-2"
            >
              <span class="text-caption text-white">v{{ version.versionNumber }}</span>
            </v-avatar>
          </template>
          <v-list-item-title>
            {{ version.name }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ formatDate(version.createdAt) }}
          </v-list-item-subtitle>
          <template #append>
            <v-btn
              v-if="canEdit"
              size="x-small"
              variant="text"
              color="primary"
              :loading="restoreLoading === version.id"
              @click.stop="restoreVersion(version)"
            >
              {{ $t("general.restore") }}
            </v-btn>
          </template>
        </v-list-item>

        <!-- Expanded diff view -->
        <v-expand-transition>
          <div v-if="expandedVersion === version.id && currentDiff">
            <v-card
              variant="outlined"
              class="mx-4 mb-2"
            >
              <v-card-text class="pa-3">
                <!-- No changes -->
                <div
                  v-if="isDiffEmpty(currentDiff)"
                  class="text-caption text-grey"
                >
                  {{ $t("recipe.version-no-changes") }}
                </div>

                <!-- Field changes -->
                <div
                  v-for="field in currentDiff.fieldsChanged"
                  :key="field.fieldName"
                  class="mb-2"
                >
                  <div class="text-caption font-weight-bold">
                    {{ field.label }}
                  </div>
                  <div
                    class="d-flex align-start"
                    style="gap: 8px"
                  >
                    <span
                      v-if="field.oldValue"
                      class="text-decoration-line-through text-red-lighten-1 text-body-2"
                    >{{ field.oldValue }}</span>
                    <span
                      v-if="field.newValue"
                      class="text-green-darken-1 text-body-2"
                    >{{ field.newValue }}</span>
                  </div>
                </div>

                <!-- Ingredients -->
                <div v-if="currentDiff.ingredientsAdded.length || currentDiff.ingredientsRemoved.length || currentDiff.ingredientsChanged.length">
                  <div class="text-caption font-weight-bold mb-1">
                    {{ $t("recipe.ingredients") }}
                  </div>
                  <div
                    v-for="ing in currentDiff.ingredientsRemoved"
                    :key="'rem-' + ing"
                    class="text-decoration-line-through text-red-lighten-1 text-body-2"
                  >
                    - {{ ing }}
                  </div>
                  <div
                    v-for="ing in currentDiff.ingredientsAdded"
                    :key="'add-' + ing"
                    class="text-green-darken-1 text-body-2"
                  >
                    + {{ ing }}
                  </div>
                  <div
                    v-for="ing in currentDiff.ingredientsChanged"
                    :key="'chg-' + ing.position"
                    class="text-body-2"
                  >
                    <span class="text-decoration-line-through text-red-lighten-1">{{ ing.oldText }}</span>
                    →
                    <span class="text-green-darken-1">{{ ing.newText }}</span>
                  </div>
                </div>

                <!-- Instructions -->
                <div
                  v-if="currentDiff.instructionsAdded.length || currentDiff.instructionsRemoved.length || currentDiff.instructionsChanged.length"
                  class="mt-2"
                >
                  <div class="text-caption font-weight-bold mb-1">
                    {{ $t("recipe.instructions") }}
                  </div>
                  <div
                    v-for="ins in currentDiff.instructionsRemoved"
                    :key="'rem-' + ins"
                    class="text-decoration-line-through text-red-lighten-1 text-body-2 text-truncate"
                  >
                    - {{ ins }}
                  </div>
                  <div
                    v-for="ins in currentDiff.instructionsAdded"
                    :key="'add-' + ins"
                    class="text-green-darken-1 text-body-2 text-truncate"
                  >
                    + {{ ins }}
                  </div>
                  <div
                    v-for="ins in currentDiff.instructionsChanged"
                    :key="'chg-' + ins.position"
                    class="text-body-2"
                  >
                    <div class="text-decoration-line-through text-red-lighten-1 text-truncate">
                      {{ ins.oldText }}
                    </div>
                    <div class="text-green-darken-1 text-truncate">
                      {{ ins.newText }}
                    </div>
                  </div>
                </div>

                <!-- Categories/Tags -->
                <div
                  v-if="currentDiff.categoriesAdded.length || currentDiff.categoriesRemoved.length"
                  class="mt-2"
                >
                  <div class="text-caption font-weight-bold mb-1">
                    {{ $t("recipe.categories") }}
                  </div>
                  <v-chip
                    v-for="c in currentDiff.categoriesRemoved"
                    :key="'crem-' + c"
                    size="x-small"
                    color="red"
                    class="mr-1"
                  >
                    - {{ c }}
                  </v-chip>
                  <v-chip
                    v-for="c in currentDiff.categoriesAdded"
                    :key="'cadd-' + c"
                    size="x-small"
                    color="green"
                    class="mr-1"
                  >
                    + {{ c }}
                  </v-chip>
                </div>
                <div
                  v-if="currentDiff.tagsAdded.length || currentDiff.tagsRemoved.length"
                  class="mt-2"
                >
                  <div class="text-caption font-weight-bold mb-1">
                    {{ $t("recipe.tags") }}
                  </div>
                  <v-chip
                    v-for="t in currentDiff.tagsRemoved"
                    :key="'trem-' + t"
                    size="x-small"
                    color="red"
                    class="mr-1"
                  >
                    - {{ t }}
                  </v-chip>
                  <v-chip
                    v-for="t in currentDiff.tagsAdded"
                    :key="'tadd-' + t"
                    size="x-small"
                    color="green"
                    class="mr-1"
                  >
                    + {{ t }}
                  </v-chip>
                </div>
              </v-card-text>
            </v-card>
          </div>
        </v-expand-transition>

        <v-divider
          v-if="idx < versions.length - 1"
        />
      </template>
    </v-list>
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";

interface RecipeVersionSummary {
  id: string;
  recipeId: string;
  userId: string | null;
  groupId: string;
  versionNumber: number;
  name: string;
  createdAt: string | null;
}

interface RecipeDiff {
  versionId: string | null;
  compareTo: string;
  fieldsChanged: { fieldName: string; label: string; oldValue: string | null; newValue: string | null }[];
  ingredientsAdded: string[];
  ingredientsRemoved: string[];
  ingredientsChanged: { position: number; oldText: string | null; newText: string | null }[];
  instructionsAdded: string[];
  instructionsRemoved: string[];
  instructionsChanged: { position: number; oldText: string | null; newText: string | null }[];
  categoriesAdded: string[];
  categoriesRemoved: string[];
  tagsAdded: string[];
  tagsRemoved: string[];
}

const props = defineProps<{
  slug: string;
  canEdit: boolean;
  inline?: boolean;
}>();

const emit = defineEmits<{
  (e: "restored"): void;
}>();

const api = useUserApi();
const i18n = useI18n();

const versions = ref<RecipeVersionSummary[]>([]);
const expandedVersion = ref<string | null>(null);
const currentDiff = ref<RecipeDiff | null>(null);
const diffLoading = ref(false);
const restoreLoading = ref<string | null>(null);

async function loadVersions() {
  const { data } = await api.recipes.requests.get<RecipeVersionSummary[]>(`/api/recipes/${props.slug}/versions`);
  if (data) {
    versions.value = data;
  }
}

async function toggleVersion(version: RecipeVersionSummary) {
  if (expandedVersion.value === version.id) {
    expandedVersion.value = null;
    currentDiff.value = null;
    return;
  }

  expandedVersion.value = version.id;
  diffLoading.value = true;
  const { data } = await api.recipes.requests.get<RecipeDiff>(`/api/recipes/${props.slug}/versions/${version.id}/diff?compare_to=current`);
  if (data) {
    currentDiff.value = data;
  }
  diffLoading.value = false;
}

async function restoreVersion(version: RecipeVersionSummary) {
  restoreLoading.value = version.id;
  const { data } = await api.recipes.requests.post<any>(`/api/recipes/${props.slug}/versions/${version.id}/restore`, {});
  if (data) {
    alert.success(i18n.t("recipe.version-restored", { version: version.versionNumber }));
    emit("restored");
  }
  restoreLoading.value = null;
}

function isDiffEmpty(diff: RecipeDiff): boolean {
  return (
    diff.fieldsChanged.length === 0
    && diff.ingredientsAdded.length === 0
    && diff.ingredientsRemoved.length === 0
    && diff.ingredientsChanged.length === 0
    && diff.instructionsAdded.length === 0
    && diff.instructionsRemoved.length === 0
    && diff.instructionsChanged.length === 0
    && diff.categoriesAdded.length === 0
    && diff.categoriesRemoved.length === 0
    && diff.tagsAdded.length === 0
    && diff.tagsRemoved.length === 0
  );
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

onMounted(loadVersions);
watch(() => props.slug, loadVersions);
</script>
