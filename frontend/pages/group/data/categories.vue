<template>
  <div>
    <!-- Create Dialog -->
    <BaseDialog
      v-model="state.createDialog"
      :title="$t('data-pages.categories.new-category')"
      :icon="$globals.icons.categories"
      can-submit
      @submit="createCategory"
    >
      <v-card-text>
        <v-form ref="domNewCategoryForm">
          <v-text-field
            v-model="createTarget.name"
            autofocus
            :label="$t('general.name')"
            :rules="[validators.required]"
          />
        </v-form>
      </v-card-text>
    </BaseDialog>

    <!-- Edit Dialog -->
    <BaseDialog
      v-model="state.editDialog"
      :icon="$globals.icons.categories"
      :title="$t('data-pages.categories.edit-category')"
      :submit-text="$t('general.save')"
      can-submit
      @submit="editSaveCategory"
    >
      <v-card-text v-if="editTarget">
        <div class="mt-4">
          <v-text-field v-model="editTarget.name" :label="$t('general.name')" />
        </div>
      </v-card-text>
    </BaseDialog>

    <!-- Bulk Delete Dialog -->
    <BaseDialog
      v-model="state.bulkDeleteDialog"
      width="650px"
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="deleteSelected"
    >
      <v-card-text>
        <p class="h4">
          {{ $t('general.confirm-delete-generic-items') }}
        </p>
        <v-card variant="outlined">
          <v-virtual-scroll height="400" item-height="25" :items="bulkDeleteTarget">
            <template #default="{ item }">
              <v-list-item class="pb-2">
                <v-list-item-title>{{ item.name }}</v-list-item-title>
              </v-list-item>
            </template>
          </v-virtual-scroll>
        </v-card>
      </v-card-text>
    </BaseDialog>

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
import { useCategoryStore, useCategoryData } from "~/composables/store";
import type { RecipeCategory } from "~/lib/api/types/recipe";
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
    const categoryData = useCategoryData();
    const categoryStore = useCategoryStore();

    // ============================================================
    // Create Category

    async function createCategory() {
      await categoryStore.actions.createOne({
        name: categoryData.data.name,
        slug: "",
      });
      categoryData.reset();
      state.createDialog = false;
    }

    // ============================================================
    // Edit Category

    const editTarget = ref<RecipeCategory | null>(null);

    function editEventHandler(item: RecipeCategory) {
      state.editDialog = true;
      editTarget.value = item;
    }

    async function editSaveCategory() {
      if (!editTarget.value) {
        return;
      }
      await categoryStore.actions.updateOne(editTarget.value);
      state.editDialog = false;
    }

    return {
      state,
      tableConfig,
      tableHeaders,
      categories: categoryStore.store,
      categoryStore: categoryStore,
      validators,

      // create
      createTarget: categoryData.data,
      createCategory,

      // edit
      editTarget,
      editEventHandler,
      editSaveCategory,
    };
  },
});
</script>
