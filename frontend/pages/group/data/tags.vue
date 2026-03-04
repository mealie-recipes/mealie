<template>
  <div>
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
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="tagStore.actions.deleteOne"
      @bulk-action="handleBulkAction"
    />
  </div>
</template>

<script setup lang="ts">
import { validators } from "~/composables/use-validators";
import { useTagStore } from "~/composables/store";
import { fieldTypes } from "~/composables/forms";
import type { AutoFormItems } from "~/types/auto-forms";
import type { RecipeTag } from "~/lib/api/types/recipe";
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
const tagStore = useTagStore();

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
  await tagStore.actions.updateOne(editFormData);
  editForm.data = {} as RecipeTag;
}

// ============================================================
// Bulk Actions
async function handleBulkAction(event: string, items: RecipeTag[]) {
  if (event === "delete-selected") {
    const ids = items.filter(item => item.id != null).map(item => item.id!);
    await tagStore.actions.deleteMany(ids);
  }
}
</script>
