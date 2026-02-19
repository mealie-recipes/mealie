<template>
  <div>
    <DataPage
      :icon="$globals.icons.categories"
      :title="$t('data-pages.categories.category-data')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="categories"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      @delete-one="categoryStore.actions.deleteOne"
      @delete-many="categoryStore.actions.deleteMany"
    />
  </div>
</template>

<script lang="ts">
import { validators } from "~/composables/use-validators";
import { useCategoryStore } from "~/composables/store";
import type { DataPageTableHeader, DataPageTableConfig } from "~/components/Domain/Group/DataPage.vue";

export default defineNuxtComponent({
  setup() {
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

    const state = reactive({
      createDialog: false,
      editDialog: false,
      deleteDialog: false,
      bulkDeleteDialog: false,
    });
    const categoryStore = useCategoryStore();

    return {
      state,
      tableConfig,
      tableHeaders,
      categories: categoryStore.store,
      categoryStore: categoryStore,
      validators,
    };
  },
});
</script>
