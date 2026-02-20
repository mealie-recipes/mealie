<template>
  <div>
    <GroupDataPage
      :icon="$globals.icons.tags"
      :title="$t('data-pages.tags.tag-data')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="tagStore.store.value || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="tagStore.actions.deleteOne"
      @delete-many="tagStore.actions.deleteMany"
    />
  </div>
</template>

<script setup lang="ts">
import { validators } from "~/composables/use-validators";
import { useTagStore } from "~/composables/store";
import { fieldTypes } from "~/composables/forms";
import type { AutoFormItems } from "~/types/auto-forms";
import type { RecipeTag } from "~/lib/api/types/recipe";
import type { GroupDataPageTableHeader, GroupDataPageTableConfig } from "~/components/Domain/Group/GroupDataPage.vue";

const i18n = useI18n();

const tableConfig: GroupDataPageTableConfig = {
  hideColumns: true,
  canExport: true,
};
const tableHeaders: GroupDataPageTableHeader[] = [
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
</script>
