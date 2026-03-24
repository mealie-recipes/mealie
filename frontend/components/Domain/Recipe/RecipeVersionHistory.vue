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
              size="x-small"
              variant="text"
              color="info"
              class="mr-1"
              @click.stop="viewFullVersion(version)"
            >
              {{ $t("general.view") }}
            </v-btn>
            <v-btn
              v-if="canEdit"
              size="x-small"
              variant="text"
              color="primary"
              :loading="restoreLoading === version.id"
              @click.stop="confirmRestore(version)"
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
                <div
                  v-if="isDiffEmpty(currentDiff)"
                  class="text-caption text-grey"
                >
                  {{ $t("recipe.version-no-changes") }}
                </div>

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
                    class="text-decoration-line-through text-red-lighten-1 text-body-2"
                  >
                    - {{ ins }}
                  </div>
                  <div
                    v-for="ins in currentDiff.instructionsAdded"
                    :key="'add-' + ins"
                    class="text-green-darken-1 text-body-2"
                  >
                    + {{ ins }}
                  </div>
                  <div
                    v-for="ins in currentDiff.instructionsChanged"
                    :key="'chg-' + ins.position"
                    class="text-body-2"
                  >
                    <div class="text-decoration-line-through text-red-lighten-1">
                      {{ ins.oldText }}
                    </div>
                    <div class="text-green-darken-1">
                      {{ ins.newText }}
                    </div>
                  </div>
                </div>

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

    <!-- Full recipe view dialog -->
    <v-dialog
      v-model="viewDialog"
      width="800"
      scrollable
    >
      <v-card v-if="viewingSnapshot">
        <v-card-title class="d-flex align-center justify-space-between">
          <span>
            v{{ viewingVersion?.versionNumber }} — {{ viewingSnapshot.name }}
          </span>
          <v-chip
            size="small"
            color="grey"
          >
            {{ formatDate(viewingVersion?.createdAt || null) }}
          </v-chip>
        </v-card-title>
        <v-divider />
        <v-card-text style="max-height: 70vh; overflow-y: auto;">
          <!-- Description -->
          <div
            v-if="viewingSnapshot.description"
            class="mb-4 text-body-1"
          >
            {{ viewingSnapshot.description }}
          </div>

          <!-- Times -->
          <div
            v-if="viewingSnapshot.prep_time || viewingSnapshot.cook_time || viewingSnapshot.total_time"
            class="mb-4"
          >
            <v-chip
              v-if="viewingSnapshot.prep_time"
              size="small"
              class="mr-1"
            >
              Prep: {{ viewingSnapshot.prep_time }}
            </v-chip>
            <v-chip
              v-if="viewingSnapshot.cook_time"
              size="small"
              class="mr-1"
            >
              Cook: {{ viewingSnapshot.cook_time }}
            </v-chip>
            <v-chip
              v-if="viewingSnapshot.total_time"
              size="small"
              class="mr-1"
            >
              Total: {{ viewingSnapshot.total_time }}
            </v-chip>
          </div>

          <!-- Yield -->
          <div
            v-if="viewingSnapshot.recipe_yield || viewingSnapshot.recipe_servings"
            class="mb-4 text-body-2"
          >
            <strong>{{ $t("recipe.servings") }}:</strong>
            {{ viewingSnapshot.recipe_servings || viewingSnapshot.recipe_yield || '' }}
            {{ viewingSnapshot.recipe_yield && viewingSnapshot.recipe_servings ? `(${viewingSnapshot.recipe_yield})` : '' }}
          </div>

          <!-- Ingredients -->
          <div v-if="viewingSnapshot.recipe_ingredient?.length">
            <h3 class="text-h6 mb-2">
              {{ $t("recipe.ingredients") }}
            </h3>
            <ul class="mb-4">
              <li
                v-for="(ing, i) in viewingSnapshot.recipe_ingredient"
                :key="i"
                class="text-body-2"
              >
                <template v-if="ing.title">
                  <strong>{{ ing.title }}</strong>
                </template>
                <template v-else>
                  {{ formatIngredient(ing) }}
                </template>
              </li>
            </ul>
          </div>

          <!-- Instructions -->
          <div v-if="viewingSnapshot.recipe_instructions?.length">
            <h3 class="text-h6 mb-2">
              {{ $t("recipe.instructions") }}
            </h3>
            <ol class="mb-4">
              <li
                v-for="(step, i) in viewingSnapshot.recipe_instructions"
                :key="i"
                class="text-body-2 mb-2"
              >
                <template v-if="step.title">
                  <strong>{{ step.title }}</strong><br>
                </template>
                {{ step.text }}
              </li>
            </ol>
          </div>

          <!-- Notes -->
          <div v-if="viewingSnapshot.notes?.length">
            <h3 class="text-h6 mb-2">
              {{ $t("recipe.notes") }}
            </h3>
            <div
              v-for="(note, i) in viewingSnapshot.notes"
              :key="i"
              class="mb-2"
            >
              <strong v-if="note.title">{{ note.title }}:</strong>
              {{ note.text }}
            </div>
          </div>

          <!-- Categories/Tags -->
          <div
            v-if="viewingSnapshot.recipe_category?.length || viewingSnapshot.tags?.length"
            class="mt-4"
          >
            <v-chip
              v-for="cat in (viewingSnapshot.recipe_category || [])"
              :key="'cat-' + (cat.name || cat.slug)"
              size="small"
              color="primary"
              class="mr-1 mb-1"
            >
              {{ cat.name || cat.slug }}
            </v-chip>
            <v-chip
              v-for="tag in (viewingSnapshot.tags || [])"
              :key="'tag-' + (tag.name || tag.slug)"
              size="small"
              color="secondary"
              class="mr-1 mb-1"
            >
              {{ tag.name || tag.slug }}
            </v-chip>
          </div>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="viewDialog = false"
          >
            {{ $t("general.close") }}
          </v-btn>
          <v-btn
            v-if="canEdit"
            color="primary"
            variant="elevated"
            :loading="restoreLoading === viewingVersion?.id"
            @click="confirmRestore(viewingVersion!)"
          >
            {{ $t("general.restore") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Restore confirmation dialog -->
    <v-dialog
      v-model="restoreDialog"
      max-width="450"
    >
      <v-card>
        <v-card-title>{{ $t("recipe.version-restore-confirm-title") }}</v-card-title>
        <v-card-text>
          {{ $t("recipe.version-restore-confirm", { version: restoreTarget?.versionNumber }) }}
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="restoreDialog = false"
          >
            {{ $t("general.cancel") }}
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="restoreLoading === restoreTarget?.id"
            @click="doRestore"
          >
            {{ $t("general.restore") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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

interface RecipeVersionFull {
  id: string;
  versionNumber: number;
  name: string;
  createdAt: string | null;
  snapshot: string;
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

// Full view dialog
const viewDialog = ref(false);
const viewingVersion = ref<RecipeVersionSummary | null>(null);
const viewingSnapshot = ref<any>(null);

// Restore confirmation
const restoreDialog = ref(false);
const restoreTarget = ref<RecipeVersionSummary | null>(null);

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

async function viewFullVersion(version: RecipeVersionSummary) {
  const { data } = await api.recipes.requests.get<RecipeVersionFull>(`/api/recipes/${props.slug}/versions/${version.id}`);
  if (data) {
    viewingVersion.value = version;
    try {
      viewingSnapshot.value = JSON.parse(data.snapshot);
    }
    catch {
      viewingSnapshot.value = null;
    }
    viewDialog.value = true;
  }
}

function confirmRestore(version: RecipeVersionSummary) {
  restoreTarget.value = version;
  restoreDialog.value = true;
}

async function doRestore() {
  if (!restoreTarget.value) return;
  restoreLoading.value = restoreTarget.value.id;
  const { data } = await api.recipes.requests.post<any>(`/api/recipes/${props.slug}/versions/${restoreTarget.value.id}/restore`, {});
  if (data) {
    alert.success(i18n.t("recipe.version-restored", { version: restoreTarget.value.versionNumber }));
    restoreDialog.value = false;
    viewDialog.value = false;
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

function formatIngredient(ing: any): string {
  const parts: string[] = [];
  if (ing.quantity) {
    const q = ing.quantity;
    parts.push(q === Math.floor(q) ? String(Math.floor(q)) : String(q));
  }
  if (ing.unit?.name) parts.push(ing.unit.name);
  if (ing.food?.name) parts.push(ing.food.name);
  if (ing.note) {
    if (parts.length) parts.push(`- ${ing.note}`);
    else parts.push(ing.note);
  }
  return parts.join(" ") || ing.original_text || "";
}

onMounted(loadVersions);
watch(() => props.slug, loadVersions);
</script>
