<template>
  <div>
    <!-- Create Dialog -->
    <BaseDialog
      v-model="state.createDialog"
      :title="$t('data-pages.tags.new-tag')"
      :icon="$globals.icons.tags"
      can-submit
      @submit="createTag"
    >
      <v-card-text>
        <v-form ref="domNewTagForm">
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
      :icon="$globals.icons.tags"
      :title="$t('data-pages.tags.edit-tag')"
      :submit-text="$t('general.save')"
      @submit="editSaveTag"
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
      @confirm="deleteTag"
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
      :icon="$globals.icons.tags"
      section
      :title="$t('data-pages.tags.tag-data')"
    />
    <CrudTable
      v-model:headers="tableHeaders"
      :table-config="tableConfig"
      :data="tags || []"
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
import { useTagStore, useTagData } from "~/composables/store";
import type { RecipeTag } from "~/lib/api/types/admin";

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

    const tagData = useTagData();
    const tagStore = useTagStore();

    // ============================================================
    // Create Tag

    async function createTag() {
      await tagStore.actions.createOne({
        name: tagData.data.name,
        slug: "",
      });
      tagData.reset();
      state.createDialog = false;
    }

    // ============================================================
    // Edit Tag

    const editTarget = ref<RecipeTag | null>(null);

    function editEventHandler(item: RecipeTag) {
      state.editDialog = true;
      editTarget.value = item;
    }

    async function editSaveTag() {
      if (!editTarget.value) {
        return;
      }
      await tagStore.actions.updateOne(editTarget.value);
      state.editDialog = false;
    }

    // ============================================================
    // Delete Tag

    const deleteTarget = ref<RecipeTag | null>(null);

    function deleteEventHandler(item: RecipeTag) {
      state.deleteDialog = true;
      deleteTarget.value = item;
    }

    async function deleteTag() {
      if (!deleteTarget.value || deleteTarget.value.id === undefined) {
        return;
      }
      await tagStore.actions.deleteOne(deleteTarget.value.id!);
      state.deleteDialog = false;
    }

    // ============================================================
    // Bulk Delete Tag
    const bulkDeleteTarget = ref<RecipeTag[]>([]);
    function bulkDeleteEventHandler(selection: RecipeTag[]) {
      bulkDeleteTarget.value = selection;
      state.bulkDeleteDialog = true;
    }

    async function deleteSelected() {
      for (const item of bulkDeleteTarget.value) {
        if (!item.id) {
          continue;
        }
        await tagStore.actions.deleteOne(item.id);
      }
      bulkDeleteTarget.value = [];
    }

    return {
      state,
      tableConfig,
      tableHeaders,
      tags: tagStore.store,
      validators,

      // create
      createTarget: tagData.data,
      createTag,

      // edit
      editTarget,
      editEventHandler,
      editSaveTag,

      // delete
      deleteTarget,
      deleteEventHandler,
      deleteTag,

      // bulk delete
      bulkDeleteTarget,
      bulkDeleteEventHandler,
      deleteSelected,
    };
  },
});
</script>
