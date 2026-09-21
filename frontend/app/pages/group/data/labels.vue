<template>
  <div>
    <GroupDataPage
      :icon="$globals.icons.tags"
      :title="$t('data-pages.labels.labels')"
      :create-title="$t('data-pages.labels.new-label')"
      :edit-title="$t('data-pages.labels.edit-label')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="labelStore.store.value || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="labelStore.actions.deleteOne"
      @bulk-action="handleBulkAction"
    >
      <template #[`item.name`]="{ item }">
        <MultiPurposeLabel
          v-if="item"
          :label="item"
        >
          {{ item.name }}
        </MultiPurposeLabel>
      </template>

      <template #create-dialog-top>
        <MultiPurposeLabel v-if="createForm.data.name" :label="createForm.data" class="my-2" />
      </template>

      <template #edit-dialog-top>
        <MultiPurposeLabel v-if="editForm.data.name" :label="editForm.data" class="my-2" />
      </template>
    </GroupDataPage>
  </div>
</template>

<script setup lang="ts">
import { validators } from "~/composables/use-validators";
import MultiPurposeLabel from "~/components/Domain/ShoppingList/MultiPurposeLabel.vue";
import { fieldTypes } from "~/composables/forms";
import type { MultiPurposeLabelSummary } from "~/lib/api/types/labels";
import type { AutoFormItems } from "~/types/auto-forms";
import { useLabelStore } from "~/composables/store";
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

const labelStore = useLabelStore();

// ============================================================
// Form items (shared)
const formItems: AutoFormItems = [
  {
    label: i18n.t("general.name"),
    varName: "name",
    type: fieldTypes.TEXT,
    rules: [validators.required],
  },
  {
    label: i18n.t("general.color"),
    varName: "color",
    type: fieldTypes.COLOR,
  },
];

// ============================================================
// Create
const createForm = reactive({
  items: formItems,
  data: {
    name: "",
    color: "",
  } as MultiPurposeLabelSummary,
});

async function handleCreate(createFormData: MultiPurposeLabelSummary) {
  await labelStore.actions.createOne(createFormData);
  createForm.data = { name: "", color: "#7417BE" } as MultiPurposeLabelSummary;
}

// ============================================================
// Edit
const editForm = reactive({
  items: formItems,
  data: {} as MultiPurposeLabelSummary,
});

async function handleEdit(editFormData: MultiPurposeLabelSummary) {
  await labelStore.actions.updateOne(editFormData);
  editForm.data = {} as MultiPurposeLabelSummary;
}

// ============================================================
// Bulk Actions
async function handleBulkAction(event: string, items: MultiPurposeLabelSummary[]) {
  if (event === "delete-selected") {
    const ids = items.filter(item => item.id != null).map(item => item.id!);
    await labelStore.actions.deleteMany(ids);
  }
}
</script>
