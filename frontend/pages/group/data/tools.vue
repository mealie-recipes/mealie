<template>
  <div>
    <GroupDataPage
      :icon="$globals.icons.tools"
      :title="$t('data-pages.tools.tool-data')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="tools || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="toolStore.actions.deleteOne"
      @delete-many="toolStore.actions.deleteMany"
    />
  </div>
</template>

<script setup lang="ts">
import { validators } from "~/composables/use-validators";
import { fieldTypes } from "~/composables/forms";
import type { AutoFormItems } from "~/types/auto-forms";
import { useToolStore } from "~/composables/store";
import type { RecipeTool, RecipeToolCreate } from "~/lib/api/types/recipe";
import type { GroupDataPageTableHeader, GroupDataPageTableConfig } from "~/components/Domain/Group/GroupDataPage.vue";

interface RecipeToolWithOnHand extends RecipeTool {
  onHand: boolean;
}

const i18n = useI18n();
const tableConfig = {
  hideColumns: true,
  canExport: true,
};
const tableHeaders = [
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
    text: i18n.t("tool.on-hand"),
    value: "onHand",
    show: true,
    sortable: true,
  },
];

const auth = useMealieAuth();
const userHousehold = computed(() => auth.user.value?.householdSlug || "");
const toolStore = useToolStore();
const tools = computed(() => toolStore.store.value.map((tools) => {
  const onHand = tools.householdsWithTool?.includes(userHousehold.value) || false;
  return { ...tools, onHand } as RecipeToolWithOnHand;
}));

// ============================================================
// Form items (shared)
const formItems = [
  {
    label: i18n.t("general.name"),
    varName: "name",
    type: fieldTypes.TEXT,
    rules: [validators.required],
  },
  {
    label: i18n.t("tool.on-hand"),
    varName: "onHand",
    type: fieldTypes.BOOLEAN,
  },
] as AutoFormItems;

// ============================================================
// Create
const createForm = reactive({
  items: formItems,
  data: { name: "", onHand: false } as RecipeToolCreate,
});

async function handleCreate(createFormData: RecipeToolCreate) {
  // TODO: The store use RecipeToolCreate or make id/slug optional as in categories and tags
  await toolStore.actions.createOne({ name: createFormData.name, householdsWithTool: createFormData.onHand ? [userHousehold.value] : [] } as RecipeToolCreate);
  createForm.data = { name: "", onHand: false } as RecipeToolCreate;
}

// ============================================================
// Edit
const editForm = reactive({
  items: formItems,
  data: {} as RecipeToolWithOnHand,
});

async function handleEdit(editFormData: RecipeToolWithOnHand) {
  // if list of households is undefined default to empty array
  if (!editFormData.householdsWithTool) {
    editFormData.householdsWithTool = [];
  }

  if (editFormData.onHand && !editFormData.householdsWithTool.includes(userHousehold.value)) {
    editFormData.householdsWithTool.push(userHousehold.value);
  }
  else if (!editFormData.onHand && editFormData.householdsWithTool.includes(userHousehold.value)) {
    const idx = editFormData.householdsWithTool.indexOf(userHousehold.value);
    if (idx !== -1) editFormData.householdsWithTool.splice(idx, 1);
  }

  await toolStore.actions.updateOne({ ...editFormData, id: editFormData.id } as RecipeTool);
  editForm.data = {} as RecipeToolWithOnHand;
}
</script>
