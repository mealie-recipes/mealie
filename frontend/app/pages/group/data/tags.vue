<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog
      v-model="mergeDialog"
      bottom-sheet
      :icon="$globals.icons.tags"
      :title="$t('data-pages.tags.combine-tag')"
      can-confirm
      @confirm="mergeTags"
      @close="resetMergeDialog"
    >
      <v-card-text>
        <div>
          {{ $t("data-pages.tags.merge-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="fromTag"
          return-object
          :items="tagStore.store.value"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.tags.source-tag')"
        />
        <v-autocomplete
          v-model="toTag"
          return-object
          :items="tagStore.store.value"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.tags.target-tag')"
        />

        <template v-if="canMerge && fromTag && toTag">
          <div class="text-center">
            {{ $t("data-pages.tags.merge-tag-example", { tag1: fromTag.name, tag2: toTag.name }) }}
          </div>
        </template>
      </v-card-text>
    </BaseDialog>

    <!-- Delete Unused Dialog -->
    <BaseDialog
      v-model="deleteUnusedDialog"
      bottom-sheet
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="confirmDeleteUnused"
    >
      <v-card-text>
        {{ $t('data-pages.tags.delete-unused-confirm', { count: unusedTagIds.length }, unusedTagIds.length) }}
        <ul style="margin: 0.5rem 0 0; padding-left: 1.25rem; font-size: 0.85rem; color: rgba(var(--v-theme-on-surface), 0.7); line-height: 1.8;">
          <li v-for="name in unusedTagNamesPreview" :key="name">
            {{ name }}
          </li>
        </ul>
        <div v-if="unusedTagNamesRemaining > 0" class="text-body-2 pl-2">
          {{ $t('data-pages.delete-unused-more', { count: unusedTagNamesRemaining }) }}
        </div>
      </v-card-text>
    </BaseDialog>

    <GroupDataPage
      :icon="$globals.icons.tags"
      :title="$t('data-pages.tags.tag-data')"
      :create-title="$t('data-pages.tags.new-tag')"
      :edit-title="$t('data-pages.tags.edit-tag')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="tagStore.store.value || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      :on-edit-dialog-open="onEditDialogOpen"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="tagStore.actions.deleteOne"
      @bulk-action="handleBulkAction"
    >
      <template #[`item.recipeCount`]="{ item }">
        <NuxtLink v-if="groupSlug && item.recipeCount > 0" :to="`/g/${groupSlug}?tags=${item.id}`">{{ item.recipeCount }}</NuxtLink>
        <span v-else>{{ item.recipeCount || 0 }}</span>
      </template>

      <template #edit-dialog-bottom>
        <div v-if="editRecipes.length > 0 || editRecipesTotal > 0 || editRecipesFailure" class="mt-4">
          <div class="text-subtitle-2 mb-1">
            {{ $t("data-pages.tags.associated-recipes") }}
          </div>
          <div class="text-caption text-medium-emphasis mb-1">
            {{ $t("data-pages.tags.associated-recipes-help") }}
          </div>
          <v-chip
            v-for="recipe in editRecipes"
            :key="recipe.id"
            label
            :closable="!chipRemovalFrozen"
            class="mr-1 mt-1"
            color="accent"
            variant="flat"
            @click:close="removeRecipeChip(recipe.id!)"
          >
            {{ recipe.name }}
          </v-chip>
          <div v-if="editRecipesFailure" class="d-flex align-center text-body-2 mt-1">
            <span v-if="editRecipesFailure.urlTooLong" class="text-error">
              {{ $t("data-pages.tags.too-many-pending-removals") }}
            </span>
            <span v-else class="text-error">{{ $t("data-pages.load-recipes-failed") }}</span>
            <v-btn
              v-if="!editRecipesFailure.urlTooLong"
              variant="text"
              size="small"
              color="primary"
              class="ml-2"
              :loading="editRecipesLoading"
              @click="retryEditRecipes"
            >
              {{ $t("data-pages.retry") }}
            </v-btn>
          </div>
          <div v-if="editRecipesTotalPages > 1" class="d-flex align-center mt-2">
            <v-btn
              variant="text"
              size="small"
              :disabled="editRecipesPage <= 1 || editRecipesLoading"
              @click="loadEditRecipesPage(editRecipesPage - 1)"
            >
              {{ $t("general.previous") }}
            </v-btn>
            <span class="text-body-2 mx-2">{{ editRecipesPage }} / {{ editRecipesTotalPages }}</span>
            <v-btn
              variant="text"
              size="small"
              :disabled="editRecipesPage >= editRecipesTotalPages || editRecipesLoading"
              @click="loadEditRecipesPage(editRecipesPage + 1)"
            >
              {{ $t("general.next") }}
            </v-btn>
          </div>
        </div>
      </template>

      <template #table-button-row>
        <BaseButton @click="mergeDialog = true">
          <template #icon>
            {{ $globals.icons.externalLink }}
          </template>
          {{ $t("data-pages.combine") }}
        </BaseButton>

        <v-divider vertical class="mx-2" />

        <BaseButton color="error" :loading="loadingEmpty" @click="openDeleteUnusedDialog">
          <template #icon>
            {{ $globals.icons.broom }}
          </template>
          {{ $t("data-pages.delete-unused") }}
        </BaseButton>
      </template>
    </GroupDataPage>
  </div>
</template>

<script setup lang="ts">
import { validators } from "~/composables/use-validators";
import { useTagStore } from "~/composables/store";
import { useUserApi } from "~/composables/api";
import { fieldTypes } from "~/composables/forms";
import { normalizeFilter } from "~/composables/use-utils";
import { alert } from "~/composables/use-toast";
import type { AutoFormItems } from "~/types/auto-forms";
import type { RecipeTag, RecipeSummary } from "~/lib/api/types/recipe";
import type { RecipeSearchQuery } from "~/lib/api/user/recipes/recipe";
import type { TableHeaders, TableConfig } from "~/components/global/CrudTable.vue";

const i18n = useI18n();
const auth = useMealieAuth();
const groupSlug = computed(() => auth.user.value?.groupSlug || "");
const userApi = useUserApi();

const tableConfig: TableConfig = {
  hideColumns: true,
  canExport: true,
};
const tableHeaders: TableHeaders[] = [
  {
    text: i18n.t("general.id"),
    value: "id",
    show: false,
  },
  {
    text: i18n.t("general.name"),
    value: "name",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("data-pages.recipe-count"),
    value: "recipeCount",
    show: true,
    sortable: true,
  },
];
const tagStore = useTagStore();

onMounted(() => {
  tagStore.actions.refresh();
});

// ============================================================
// Form items (shared)
const formItems = [
  {
    label: i18n.t("general.name"),
    varName: "name",
    type: fieldTypes.TEXT,
    rules: [validators.required],
  },
] as AutoFormItems;

// ============================================================
// Create
const createForm = reactive({
  items: formItems,
  data: { name: "" } as RecipeTag,
});

async function handleCreate(createFormData: RecipeTag) {
  await tagStore.actions.createOne(createFormData);
  createForm.data.name = "";
}

// ============================================================
// Edit
const editForm = reactive({
  items: formItems,
  data: {} as RecipeTag,
});

async function handleEdit(editFormData: RecipeTag) {
  if (removedRecipeIds.value.length > 0 && editFormData.id) {
    await userApi.tags.removeFromRecipes(editFormData.id, removedRecipeIds.value);
  }
  await tagStore.actions.updateOne(editFormData);
  editForm.data = {} as RecipeTag;
  resetEditRecipes();
}

// ============================================================
// Edit Dialog: Associated Recipes
const EDIT_RECIPES_PREVIEW_LIMIT = 10;

// Every fetch excludes the recipes staged for removal on the server (`id NOT IN [...]`), so the recipes still
// on the tag form one alphabetical list that pages are cut from. A page is always fetched fresh rather than
// rebuilt locally, so a recipe staged on one page never reappears on another, and a removal is backfilled by
// fetching the single recipe at the first empty slot of the page being viewed.
const editRecipes = ref<RecipeSummary[]>([]);
const editRecipesPage = ref(1);
// recipes on the tag, not counting those staged for removal
const editRecipesTotal = ref(0);
const editRecipesTagId = ref<string | null>(null);
const editRecipesPageLoading = ref(false);
const editRecipesRefillLoading = ref(false);
const editRecipesLoading = computed(() => editRecipesPageLoading.value || editRecipesRefillLoading.value);
// the fetch that failed, so Retry repeats it; null when nothing has failed
const editRecipesFailure = shallowRef<{
  retry: () => Promise<void>;
  // a page load (first, Next or Previous) rather than a refill
  isPageLoad: boolean;
  // the request was rejected for its URL length, which only the staged-id filter can grow
  urlTooLong: boolean;
} | null>(null);
const removedRecipeIds = ref<string[]>([]);
const editRecipesTotalPages = computed(() => Math.ceil(editRecipesTotal.value / EDIT_RECIPES_PREVIEW_LIMIT));
// Removal is frozen while a page loads, so the staged set a page request was made with is still current when it
// returns, and while a failed page load is shown, so a refill can't replace its retry. It unfreezes once a page
// loads, whether by Retry or by navigating to another page.
const chipRemovalFrozen = computed(() => editRecipesPageLoading.value || !!editRecipesFailure.value?.isPageLoad);

// bumped whenever the dialog's recipe state is reset, so a response for an earlier visit is dropped
let editRecipesRequestId = 0;

function resetEditRecipes() {
  editRecipesRequestId++;
  editRecipes.value = [];
  editRecipesPage.value = 1;
  editRecipesTotal.value = 0;
  editRecipesTagId.value = null;
  editRecipesPageLoading.value = false;
  editRecipesRefillLoading.value = false;
  editRecipesFailure.value = null;
  removedRecipeIds.value = [];
}

async function fetchEditRecipes(tagId: string, page: number, perPage: number) {
  const query: RecipeSearchQuery = {
    tags: [tagId],
    page,
    perPage,
    // names are compared lower-cased; id breaks ties between recipes with the same name so pages stay stable
    orderBy: "name:asc,id:asc",
  };
  if (removedRecipeIds.value.length > 0) {
    query.queryFilter = `id NOT IN [${removedRecipeIds.value.join(", ")}]`;
  }
  // request failures come back as `error` rather than being thrown
  return await userApi.recipes.search(query);
}

function isUrlTooLongError(error: any) {
  if (removedRecipeIds.value.length === 0) {
    // without staged ids the URL is short, so this is some other failure
    return false;
  }
  const status = error?.response?.status;
  // 414 URI Too Long and 431 Request Header Fields Too Large are what proxies send; uvicorn itself rejects an
  // oversized request line with a plain-text 400, where the API's own 400s always have a JSON body
  return status === 414 || status === 431 || (status === 400 && typeof error?.response?.data === "string");
}

async function onEditDialogOpen(item: RecipeTag) {
  resetEditRecipes();
  if (!item?.id) {
    return;
  }
  editRecipesTagId.value = item.id;
  await loadEditRecipesPage(1);
}

async function loadEditRecipesPage(page: number) {
  const tagId = editRecipesTagId.value;
  if (!tagId || editRecipesLoading.value) {
    return;
  }
  const requestId = editRecipesRequestId;
  let pageGone = false;
  editRecipesPageLoading.value = true;
  try {
    const { data, error } = await fetchEditRecipes(tagId, page, EDIT_RECIPES_PREVIEW_LIMIT);
    if (requestId !== editRecipesRequestId) {
      return;
    }
    if (error || !data) {
      // the current page stays in view, and Retry asks for the same page again
      editRecipesFailure.value = {
        retry: () => loadEditRecipesPage(page),
        isPageLoad: true,
        urlTooLong: isUrlTooLongError(error),
      };
      return;
    }
    editRecipesFailure.value = null;
    editRecipesTotal.value = data.total ?? 0;
    const recipes = data.items ?? [];
    // recipes can be untagged elsewhere while the dialog is open, leaving fewer pages than there were
    pageGone = recipes.length === 0 && page > 1;
    if (!pageGone) {
      editRecipes.value = recipes;
      editRecipesPage.value = page;
    }
  }
  finally {
    if (requestId === editRecipesRequestId) {
      editRecipesPageLoading.value = false;
    }
  }

  if (pageGone) {
    await loadEditRecipesPage(Math.max(editRecipesTotalPages.value, 1));
  }
}

// Fills the empty slots at the end of the page being viewed, one recipe per fetch. Each fetch asks for the
// recipe at the first empty slot; a chip removed while it's in flight sat before that slot, so the result
// still belongs at the end of the list, and the loop then moves on to the slot the removal opened up.
async function refillEditRecipes() {
  const tagId = editRecipesTagId.value;
  if (!tagId || editRecipesLoading.value) {
    return;
  }
  const requestId = editRecipesRequestId;
  let failed = false;
  editRecipesRefillLoading.value = true;
  try {
    while (editRecipes.value.length < EDIT_RECIPES_PREVIEW_LIMIT) {
      // position of the first empty slot in the list of recipes not staged for removal
      const slot = (editRecipesPage.value - 1) * EDIT_RECIPES_PREVIEW_LIMIT + editRecipes.value.length;
      if (slot >= editRecipesTotal.value) {
        break;
      }
      const stagedBefore = removedRecipeIds.value.length;
      const { data, error } = await fetchEditRecipes(tagId, slot + 1, 1);
      if (requestId !== editRecipesRequestId) {
        return;
      }
      if (error || !data) {
        // Retry runs the refill again, which asks for the same slot
        editRecipesFailure.value = {
          retry: refillEditRecipes,
          isPageLoad: false,
          urlTooLong: isUrlTooLongError(error),
        };
        failed = true;
        break;
      }
      editRecipesFailure.value = null;
      // chips staged while the request was in flight were already subtracted locally but aren't in its total
      editRecipesTotal.value = Math.max((data.total ?? 0) - (removedRecipeIds.value.length - stagedBefore), 0);
      const recipe = data.items?.[0];
      if (!recipe?.id || editRecipes.value.some(r => r.id === recipe.id) || removedRecipeIds.value.includes(recipe.id)) {
        // only possible if the tag's recipes changed elsewhere; stop rather than ask for the same slot again
        break;
      }
      editRecipes.value.push(recipe);
    }
  }
  finally {
    if (requestId === editRecipesRequestId) {
      editRecipesRefillLoading.value = false;
    }
  }

  // the last chip on a later page was removed and nothing was left to fill it with
  if (!failed && requestId === editRecipesRequestId && editRecipes.value.length === 0 && editRecipesPage.value > 1) {
    await loadEditRecipesPage(Math.max(editRecipesTotalPages.value, 1));
  }
}

async function retryEditRecipes() {
  await editRecipesFailure.value?.retry();
}

function removeRecipeChip(recipeId: string) {
  if (chipRemovalFrozen.value || removedRecipeIds.value.includes(recipeId)) {
    return;
  }
  removedRecipeIds.value.push(recipeId);
  editRecipes.value = editRecipes.value.filter(recipe => recipe.id !== recipeId);
  editRecipesTotal.value = Math.max(editRecipesTotal.value - 1, 0);
  // a refill that's already running picks up the new empty slot itself
  refillEditRecipes();
}

// ============================================================
// Bulk Actions
async function handleBulkAction(event: string, items: RecipeTag[]) {
  if (event === "delete-selected") {
    const ids = items.filter(item => item.id != null).map(item => item.id!);
    await tagStore.actions.deleteMany(ids);
  }
}

// ============================================================
// Merge Tags
const mergeDialog = ref(false);
const fromTag = ref<RecipeTag | null>(null);
const toTag = ref<RecipeTag | null>(null);

const canMerge = computed(() => {
  return fromTag.value && toTag.value && fromTag.value.id !== toTag.value.id;
});

function resetMergeDialog() {
  fromTag.value = null;
  toTag.value = null;
}

async function mergeTags() {
  if (!canMerge.value || !fromTag.value?.id || !toTag.value?.id) {
    return;
  }

  const { data } = await userApi.tags.merge(fromTag.value.id, toTag.value.id);

  if (data) {
    fromTag.value = null;
    toTag.value = null;
    tagStore.actions.refresh();
  }
}

// ============================================================
// Delete Unused
const DELETE_UNUSED_PREVIEW_LIMIT = 10;

const deleteUnusedDialog = ref(false);
const unusedTags = ref<RecipeTag[]>([]);
const unusedTagIds = computed(() => unusedTags.value.filter(t => t.id != null).map(t => t.id!));
const unusedTagNamesPreview = computed(() => unusedTags.value.slice(0, DELETE_UNUSED_PREVIEW_LIMIT).map(t => t.name));
const unusedTagNamesRemaining = computed(() => Math.max(unusedTags.value.length - DELETE_UNUSED_PREVIEW_LIMIT, 0));
const loadingEmpty = ref(false);

async function openDeleteUnusedDialog() {
  loadingEmpty.value = true;
  const { data } = await userApi.tags.getEmpty();
  loadingEmpty.value = false;
  unusedTags.value = data ?? [];

  if (unusedTags.value.length === 0) {
    alert.info(i18n.t("data-pages.tags.no-unused-tags"));
    return;
  }

  deleteUnusedDialog.value = true;
}

async function confirmDeleteUnused() {
  await tagStore.actions.deleteMany(unusedTagIds.value);
  unusedTags.value = [];
}
</script>
