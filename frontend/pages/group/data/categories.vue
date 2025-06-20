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
          <v-text-field
            v-model="editTarget.name"
            :label="$t('general.name')"
          />
        </div>
      </v-card-text>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="state.deleteDialog"
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="deleteCategory"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
        <p
          v-if="deleteTarget"
          class="mt-4 ml-4"
        >
          {{ deleteTarget.name }}
        </p>
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
          <v-virtual-scroll
            height="400"
            item-height="25"
            :items="bulkDeleteTarget"
          >
            <template #default="{ item }">
              <v-list-item class="pb-2">
                <v-list-item-title>{{ item.name }}</v-list-item-title>
              </v-list-item>
            </template>
          </v-virtual-scroll>
        </v-card>
      </v-card-text>
    </BaseDialog>

    <!-- Data Table -->
    <BaseCardSectionTitle
      :icon="$globals.icons.categories"
      section
      :title="$t('data-pages.categories.category-data')"
    />
    <CrudTable
      v-model:headers="tableHeaders"
      :table-config="tableConfig"
      :data="categories || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      initial-sort="name"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
      @delete-selected="bulkDeleteEventHandler"
    >
      <template #button-row>
        <BaseButton
          create
          @click="state.createDialog = true"
        >
          {{ $t("general.create") }}
        </BaseButton>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { validators } from "~/composables/use-validators";
import { useCategoryStore, useCategoryData } from "~/composables/store";
import type { RecipeCategory } from "~/lib/api/types/recipe";

export default defineNuxtComponent({
  setup() {
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

    // ============================================================
    // Delete Category

    const deleteTarget = ref<RecipeCategory | null>(null);

    function deleteEventHandler(item: RecipeCategory) {
      state.deleteDialog = true;
      deleteTarget.value = item;
    }

    async function deleteCategory() {
      if (!deleteTarget.value || deleteTarget.value.id === undefined) {
        return;
      }
      await categoryStore.actions.deleteOne(deleteTarget.value.id);
      state.deleteDialog = false;
    }

    // ============================================================
    // Bulk Delete Category
    const bulkDeleteTarget = ref<RecipeCategory[]>([]);
    function bulkDeleteEventHandler(selection: RecipeCategory[]) {
      bulkDeleteTarget.value = selection;
      state.bulkDeleteDialog = true;
    }

    async function deleteSelected() {
      for (const item of bulkDeleteTarget.value) {
        if (!item.id) {
          continue;
        }
        await categoryStore.actions.deleteOne(item.id);
      }
      bulkDeleteTarget.value = [];
    }

    return {
      state,
      tableConfig,
      tableHeaders,
      categories: categoryStore.store,
      validators,

      // create
      createTarget: categoryData.data,
      createCategory,

      // edit
      editTarget,
      editEventHandler,
      editSaveCategory,

      // delete
      deleteTarget,
      deleteEventHandler,
      deleteCategory,

      // bulk delete
      bulkDeleteTarget,
      bulkDeleteEventHandler,
      deleteSelected,
    };
  },
});
</script>
