<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog
      v-model="mergeDialog"
      :icon="$globals.icons.categories"
      :title="$t('data-pages.categories.combine-category')"
      can-confirm
      @confirm="mergeCategories"
      @close="resetMergeDialog"
    >
      <v-card-text>
        <div>
          {{ $t("data-pages.categories.merge-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="fromCategory"
          return-object
          :items="categoryStore.store.value"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.categories.source-category')"
        />
        <v-autocomplete
          v-model="toCategory"
          return-object
          :items="categoryStore.store.value"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.categories.target-category')"
        />

        <template v-if="canMerge && fromCategory && toCategory">
          <div class="text-center">
            {{ $t("data-pages.categories.merge-category-example", { category1: fromCategory.name, category2: toCategory.name }) }}
          </div>
        </template>
      </v-card-text>
    </BaseDialog>

    <!-- Delete Unused Dialog -->
    <BaseDialog
      v-model="deleteUnusedDialog"
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="confirmDeleteUnused"
    >
      <v-card-text>
        {{ $t('data-pages.categories.delete-unused-confirm', { count: unusedCategoryIds.length }, unusedCategoryIds.length) }}
        <ul style="margin: 0.5rem 0 0; padding-left: 1.25rem; font-size: 0.85rem; color: rgba(var(--v-theme-on-surface), 0.7); line-height: 1.8;">
          <li v-for="name in unusedCategoryNamesPreview" :key="name">
            {{ name }}
          </li>
        </ul>
        <div v-if="unusedCategoryNamesRemaining > 0" class="text-body-2 pl-2">
          {{ $t('data-pages.delete-unused-more', { count: unusedCategoryNamesRemaining }) }}
        </div>
      </v-card-text>
    </BaseDialog>

    <GroupDataPage
      :icon="$globals.icons.categories"
      :title="$t('data-pages.categories.category-data')"
      :create-title="$t('data-pages.categories.new-category')"
      :edit-title="$t('data-pages.categories.edit-category')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="categoryStore.store.value || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      :on-edit-dialog-open="onEditDialogOpen"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="categoryStore.actions.deleteOne"
      @bulk-action="handleBulkAction"
    >
      <template #[`item.recipeCount`]="{ item }">
        <NuxtLink v-if="groupSlug && item.recipeCount > 0" :to="`/g/${groupSlug}?categories=${item.id}`">{{ item.recipeCount }}</NuxtLink>
        <span v-else>{{ item.recipeCount || 0 }}</span>
      </template>

      <template #edit-dialog-bottom>
        <div v-if="editRecipes.length > 0" class="mt-4">
          <div class="text-subtitle-2 mb-1">
            {{ $t("data-pages.categories.associated-recipes") }}
          </div>
          <v-list density="compact">
            <v-list-item
              v-for="recipe in editRecipesPreview"
              :key="recipe.slug"
              :to="`/g/${groupSlug}/r/${recipe.slug}`"
              :title="recipe.name || recipe.slug"
            />
          </v-list>
          <div v-if="editRecipesRemaining > 0" class="text-body-2 pl-2">
            {{ $t('data-pages.delete-unused-more', { count: editRecipesRemaining }) }}
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
import { useCategoryStore } from "~/composables/store";
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { fieldTypes } from "~/composables/forms";
import { normalizeFilter } from "~/composables/use-utils";
import { alert } from "~/composables/use-toast";
import type { AutoFormItems } from "~/types/auto-forms";
import type { RecipeCategory, RecipeSummary } from "~/lib/api/types/recipe";
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
const categoryStore = useCategoryStore();

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
  data: { name: "" } as RecipeCategory,
});

async function handleCreate(createFormData: RecipeCategory) {
  await categoryStore.actions.createOne(createFormData);
  createForm.data.name = "";
}

// ============================================================
// Edit
const editForm = reactive({
  items: formItems,
  data: {} as RecipeCategory,
});

async function handleEdit(editFormData: RecipeCategory) {
  await categoryStore.actions.updateOne(editFormData);
  editForm.data = {} as RecipeCategory;
  editRecipes.value = [];
}

// ============================================================
// Edit Dialog: Associated Recipes
const EDIT_RECIPES_PREVIEW_LIMIT = 10;

const editRecipes = ref<RecipeSummary[]>([]);
const editRecipesPreview = computed(() => editRecipes.value.slice(0, EDIT_RECIPES_PREVIEW_LIMIT));
const editRecipesRemaining = computed(() => Math.max(editRecipes.value.length - EDIT_RECIPES_PREVIEW_LIMIT, 0));

async function onEditDialogOpen(item: RecipeCategory) {
  editRecipes.value = [];
  if (!item?.slug) {
    return;
  }
  const { data } = await userApi.categories.bySlug(item.slug);
  editRecipes.value = data?.recipes ?? [];
}

// ============================================================
// Bulk Actions
async function handleBulkAction(event: string, items: RecipeCategory[]) {
  if (event === "delete-selected") {
    const ids = items.filter(item => item.id != null).map(item => item.id!);
    await categoryStore.actions.deleteMany(ids);
  }
}

// ============================================================
// Merge Categories
const mergeDialog = ref(false);
const fromCategory = ref<RecipeCategory | null>(null);
const toCategory = ref<RecipeCategory | null>(null);

const canMerge = computed(() => {
  return fromCategory.value && toCategory.value && fromCategory.value.id !== toCategory.value.id;
});

function resetMergeDialog() {
  fromCategory.value = null;
  toCategory.value = null;
}

async function mergeCategories() {
  if (!canMerge.value || !fromCategory.value?.id || !toCategory.value?.id) {
    return;
  }

  const { data } = await userApi.categories.merge(fromCategory.value.id, toCategory.value.id);

  if (data) {
    fromCategory.value = null;
    toCategory.value = null;
    categoryStore.actions.refresh();
  }
}

// ============================================================
// Delete Unused
const DELETE_UNUSED_PREVIEW_LIMIT = 10;

const deleteUnusedDialog = ref(false);
const unusedCategories = ref<RecipeCategory[]>([]);
const unusedCategoryIds = computed(() => unusedCategories.value.filter(c => c.id != null).map(c => c.id!));
const unusedCategoryNamesPreview = computed(() =>
  unusedCategories.value.slice(0, DELETE_UNUSED_PREVIEW_LIMIT).map(c => c.name),
);
const unusedCategoryNamesRemaining = computed(() =>
  Math.max(unusedCategories.value.length - DELETE_UNUSED_PREVIEW_LIMIT, 0),
);
const loadingEmpty = ref(false);

async function openDeleteUnusedDialog() {
  loadingEmpty.value = true;
  const { data } = await userApi.categories.getEmpty();
  loadingEmpty.value = false;
  unusedCategories.value = data ?? [];

  if (unusedCategories.value.length === 0) {
    alert.info(i18n.t("data-pages.categories.no-unused-categories"));
    return;
  }

  deleteUnusedDialog.value = true;
}

async function confirmDeleteUnused() {
  await categoryStore.actions.deleteMany(unusedCategoryIds.value);
  unusedCategories.value = [];
}
</script>
