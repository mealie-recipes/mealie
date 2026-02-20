<template>
  <div>
    <DataPage
      :icon="$globals.icons.categories"
      :title="$t('data-pages.categories.category-data')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="categoryStore.store.value || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      @create-one="handleCreate"
      @delete-one="categoryStore.actions.deleteOne"
      @delete-many="categoryStore.actions.deleteMany"
    />
  </div>
</template>

<script  setup lang="ts">
import { useCategoryStore } from "~/composables/store";
import { validators } from "~/composables/use-validators";
import { fieldTypes } from "~/composables/forms";
import type { AutoFormItems } from "~/types/auto-forms";
import type { RecipeCategory } from "~/lib/api/types/recipe";
import type { DataPageTableHeader, DataPageTableConfig } from "~/components/Domain/Group/DataPage.vue";

const i18n = useI18n();
const tableConfig: DataPageTableConfig = {
  hideColumns: true,
  canExport: true,
};
const tableHeaders: Array<DataPageTableHeader> = [
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
// Create
const createForm = reactive({
  items: [
    {
      label: i18n.t("general.name"),
      varName: "name",
      type: fieldTypes.TEXT,
      rules: [validators.required],
    },
  ] as AutoFormItems,
  data: { name: "" } as RecipeCategory,
});

async function handleCreate(createFormData: RecipeCategory) {
  await categoryStore.actions.createOne(createFormData);
  createForm.data.name = "";
}
</script>
