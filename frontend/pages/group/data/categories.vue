<template>
  <div>
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
    />
  </div>
</template>

<script setup lang="ts">
import { useCategoryStore } from "~/composables/store";
import { validators } from "~/composables/use-validators";
import { fieldTypes } from "~/composables/forms";
import type { AutoFormItems } from "~/types/auto-forms";
import type { RecipeCategory } from "~/lib/api/types/recipe";
import type { TableHeaders, TableConfig } from "~/components/global/CrudTable.vue";

const i18n = useI18n();
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
</script>
