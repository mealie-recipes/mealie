<template>
  <div>
    <!-- Create Dialog -->
    <BaseDialog
      v-model="state.createDialog"
      :title="$t('data-pages.recipe-actions.new-recipe-action')"
      :icon="$globals.icons.primary"
      @submit="createAction"
    >
      <v-card-text>
        <v-form ref="domNewActionForm">
          <v-text-field
            v-model="createTarget.title"
            autofocus
            :label="$t('general.title')"
            :rules="[validators.required]"
          />
          <v-text-field
            v-model="createTarget.url"
            :label="$t('general.url')"
            :rules="[validators.required]"
          />
          <v-select
            v-model="createTarget.actionType"
            :items="actionTypeOptions"
            :label="$t('data-pages.recipe-actions.action-type')"
            :rules="[validators.required]"
          />
        </v-form>
      </v-card-text>
    </BaseDialog>

    <!-- Edit Dialog -->
    <BaseDialog
      v-model="state.editDialog"
      :icon="$globals.icons.primary"
      :title="$t('data-pages.recipe-actions.edit-recipe-action')"
      :submit-text="$tc('general.save')"
      @submit="editSaveAction"
    >
      <v-card-text v-if="editTarget">
        <div class="mt-4">
          <v-text-field v-model="editTarget.title" :label="$t('general.title')"/>
        </div>
        <div class="mt-4">
          <v-text-field v-model="editTarget.url" :label="$t('general.url')"/>
        </div>
        <div class="mt-4">
          <v-select
            v-model="editTarget.actionType"
            :items="actionTypeOptions"
            :label="$t('data-pages.recipe-actions.action-type')"
          />
        </div>
      </v-card-text>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="state.deleteDialog"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteAction"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
        <p v-if="deleteTarget" class="mt-4 ml-4">{{ deleteTarget.title }}</p>
      </v-card-text>
    </BaseDialog>

    <!-- Bulk Delete Dialog -->
    <BaseDialog
      v-model="state.bulkDeleteDialog"
      width="650px"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteSelected"
    >
      <v-card-text>
        <p class="h4">{{ $t('general.confirm-delete-generic-items') }}</p>
        <v-card outlined>
          <v-virtual-scroll height="400" item-height="25" :items="bulkDeleteTarget">
            <template #default="{ item }">
              <v-list-item class="pb-2">
                <v-list-item-content>
                  <v-list-item-title>{{ item.name }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </template>
          </v-virtual-scroll>
        </v-card>
      </v-card-text>
    </BaseDialog>

    <!-- Data Table -->
    <BaseCardSectionTitle :icon="$globals.icons.primary" section :title="$tc('data-pages.recipe-actions.recipe-actions-data')"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="actions || []"
      :bulk-actions="[{icon: $globals.icons.delete, text: $tc('general.delete'), event: 'delete-selected'}]"
      initial-sort="title"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
      @delete-selected="bulkDeleteEventHandler"
    >
      <template #button-row>
        <BaseButton create @click="state.createDialog = true">{{ $t("general.create") }}</BaseButton>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, useContext } from "@nuxtjs/composition-api";
import { validators } from "~/composables/use-validators";
import { useGroupRecipeActions, useGroupRecipeActionData } from "~/composables/use-group-recipe-actions";
import { GroupRecipeActionOut } from "~/lib/api/types/household";

export default defineComponent({
  setup() {
    const { i18n } = useContext();
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
        text: i18n.t("general.title"),
        value: "title",
        show: true,
      },
      {
        text: i18n.t("general.url"),
        value: "url",
        show: true,
      },
      {
        text: i18n.t("data-pages.recipe-actions.action-type"),
        value: "actionType",
        show: true,
      },
    ];

    const state = reactive({
      createDialog: false,
      editDialog: false,
      deleteDialog: false,
      bulkDeleteDialog: false,
    });

    const actionData = useGroupRecipeActionData();
    const actionStore = useGroupRecipeActions(null, null);
    const actionTypeOptions = ["link", "post"]


    // ============================================================
    // Create Action

    async function createAction() {
      // @ts-ignore groupId isn't required
      await actionStore.actions.createOne({
        actionType: actionData.data.actionType,
        title: actionData.data.title,
        url: actionData.data.url,
      });
      actionData.reset();
      state.createDialog = false;
    }


    // ============================================================
    // Edit Action

    const editTarget = ref<GroupRecipeActionOut | null>(null);

    function editEventHandler(item: GroupRecipeActionOut) {
      state.editDialog = true;
      editTarget.value = item;
    }

    async function editSaveAction() {
      if (!editTarget.value) {
        return;
      }
      await actionStore.actions.updateOne(editTarget.value);
      state.editDialog = false;
    }


    // ============================================================
    // Delete Action

    const deleteTarget = ref<GroupRecipeActionOut | null>(null);

    function deleteEventHandler(item: GroupRecipeActionOut) {
      state.deleteDialog = true;
      deleteTarget.value = item;
    }

    async function deleteAction() {
      if (!deleteTarget.value || deleteTarget.value.id === undefined) {
        return;
      }
      await actionStore.actions.deleteOne(deleteTarget.value.id);
      state.deleteDialog = false;
    }

    // ============================================================
    // Bulk Delete Action

    const bulkDeleteTarget = ref<GroupRecipeActionOut[]>([]);
    function bulkDeleteEventHandler(selection: GroupRecipeActionOut[]) {
      bulkDeleteTarget.value = selection;
      state.bulkDeleteDialog = true;
    }

    async function deleteSelected() {
      for (const item of bulkDeleteTarget.value) {
        await actionStore.actions.deleteOne(item.id);
      }
      bulkDeleteTarget.value = [];
    }

    return {
      state,
      tableConfig,
      tableHeaders,
      actionTypeOptions,
      actions: actionStore.recipeActions,
      validators,

      // create
      createTarget: actionData.data,
      createAction,

      // edit
      editTarget,
      editEventHandler,
      editSaveAction,

      // delete
      deleteTarget,
      deleteEventHandler,
      deleteAction,

      // bulk delete
      bulkDeleteTarget,
      bulkDeleteEventHandler,
      deleteSelected,
    };
  },
});
</script>
