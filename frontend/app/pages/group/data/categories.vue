<template>
  <div>
    <BaseDialog
      v-model="deleteUnusedDialog"
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="confirmDeleteUnused"
    >
      <v-card-text>
        Delete {{ unusedCategoryIds.length }} unused category(s)? This cannot be undone.
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
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="categoryStore.actions.deleteOne"
      @bulk-action="handleBulkAction"
    >
      <template #table-button-row>
        <BaseButton :loading="loadingEmpty" @click="openDeleteUnusedDialog">
          <template #icon>
            {{ $globals.icons.delete }}
          </template>
          Delete Unused
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
import type { AutoFormItems } from "~/types/auto-forms";
import type { RecipeCategory } from "~/lib/api/types/recipe";
import type { TableHeaders, TableConfig } from "~/components/global/CrudTable.vue";

const i18n = useI18n();
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
    text: "Recipe Count",
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
// Delete Unused
const deleteUnusedDialog = ref(false);
const unusedCategoryIds = ref<string[]>([]);
const loadingEmpty = ref(false);

async function openDeleteUnusedDialog() {
  loadingEmpty.value = true;
  const { data } = await userApi.categories.getEmpty();
  loadingEmpty.value = false;
  unusedCategoryIds.value = (data ?? []).filter(c => c.id != null).map(c => c.id!);
  deleteUnusedDialog.value = true;
}

async function confirmDeleteUnused() {
  await categoryStore.actions.deleteMany(unusedCategoryIds.value);
  unusedCategoryIds.value = [];
}
</script>
