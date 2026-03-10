<template>
  <div>
    <GroupDataPage
      :icon="$globals.icons.tags"
      :title="$t('data-pages.tag-groups.tag-group-data')"
      :create-title="$t('data-pages.tag-groups.new-tag-group')"
      :edit-title="$t('data-pages.tag-groups.edit-tag-group')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="tagGroupStore.store.value || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="tagGroupStore.actions.deleteOne"
      @bulk-action="handleBulkAction"
    >
      <template #[`item.color`]="{ item }">
        <div class="d-flex align-center ga-2">
          <div
            v-if="item.color"
            :style="{ backgroundColor: item.color, width: '18px', height: '18px', borderRadius: '50%', flexShrink: 0 }"
          />
          <span>{{ item.color }}</span>
        </div>
      </template>
    </GroupDataPage>
  </div>
</template>

<script setup lang="ts">
import { validators } from "~/composables/use-validators";
import { useTagGroupStore } from "~/composables/store";
import { fieldTypes } from "~/composables/forms";
import type { AutoFormItems } from "~/types/auto-forms";
import type { TagGroupOut } from "~/lib/api/types/recipe";
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
  {
    text: i18n.t("tag.tag-group-color"),
    value: "color",
    show: true,
  },
  {
    text: i18n.t("tag.tag-group-position"),
    value: "position",
    show: true,
    sortable: true,
  },
];

const tagGroupStore = useTagGroupStore();

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
    label: i18n.t("tag.tag-group-color"),
    varName: "color",
    type: fieldTypes.COLOR,
  },
  {
    label: i18n.t("tag.tag-group-position"),
    varName: "position",
    type: fieldTypes.TEXT,
  },
];

// ============================================================
// Create
const createForm = reactive({
  items: formItems,
  data: { name: "", color: "", position: 0 } as unknown as TagGroupOut,
});

async function handleCreate(createFormData: TagGroupOut) {
  await tagGroupStore.actions.createOne(createFormData);
  createForm.data = { name: "", color: "", position: 0 } as unknown as TagGroupOut;
}

// ============================================================
// Edit
const editForm = reactive({
  items: formItems,
  data: {} as TagGroupOut,
});

async function handleEdit(editFormData: TagGroupOut) {
  await tagGroupStore.actions.updateOne(editFormData);
  editForm.data = {} as TagGroupOut;
}

// ============================================================
// Bulk Actions
async function handleBulkAction(event: string, items: TagGroupOut[]) {
  if (event === "delete-selected") {
    for (const item of items) {
      if (item.id) await tagGroupStore.actions.deleteOne(item.id);
    }
    await tagGroupStore.actions.refresh();
  }
}
</script>
