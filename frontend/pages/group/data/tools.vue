<template>
  <div>
    <!-- Create Dialog -->
    <BaseDialog
      v-model="state.createDialog"
      :title="$t('data-pages.tools.new-tool')"
      :icon="$globals.icons.potSteam"
      @submit="createTool"
    >
      <v-card-text>
        <v-form ref="domNewToolForm">
          <v-text-field
            v-model="createTarget.name"
            autofocus
            :label="$t('general.name')"
            :rules="[validators.required]"
          ></v-text-field>
        </v-form>
      </v-card-text>

    </BaseDialog>

    <!-- Edit Dialog -->
    <BaseDialog
      v-model="state.editDialog"
      :icon="$globals.icons.potSteam"
      :title="$t('data-pages.tools.edit-tool')"
      :submit-text="$tc('general.save')"
      @submit="editSaveTool"
    >
      <v-card-text v-if="editTarget">
        <div class="mt-4">
          <v-text-field v-model="editTarget.name" :label="$t('general.name')"> </v-text-field>
        </div>
      </v-card-text>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="state.deleteDialog"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteTool"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <!-- Recipe Data Table -->
    <BaseCardSectionTitle :icon="$globals.icons.potSteam" section :title="$tc('data-pages.tools.tool-data')"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="tools || []"
      :bulk-actions="[]"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
    >
      <template #button-row>
        <BaseButton create @click="state.createDialog = true">
          <template #icon> {{ $globals.icons.potSteam }} </template>
          {{ $t("general.create") }}
        </BaseButton>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, useContext } from "@nuxtjs/composition-api";
import { validators } from "~/composables/use-validators";
import { useToolStore, useToolData } from "~/composables/store";
import { RecipeTool } from "~/lib/api/types/admin";

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
        text: i18n.t("general.name"),
        value: "name",
        show: true,
      },
    ];

    const state = reactive({
      createDialog: false,
      editDialog: false,
      deleteDialog: false,
    });

    const toolData = useToolData();
    const toolStore = useToolStore();


    // ============================================================
    // Create Tag

    async function createTool() {
      // @ts-ignore - only property really required is the name (RecipeOrganizerPage)
      await toolStore.actions.createOne({ name: toolData.data.name });
      toolData.reset();
      state.createDialog = false;
    }


    // ============================================================
    // Edit Tag

    const editTarget = ref<RecipeTool | null>(null);

    function editEventHandler(item: RecipeTool) {
      state.editDialog = true;
      editTarget.value = item;
      console.log(editTarget.value)
    }

    async function editSaveTool() {
      if (!editTarget.value) {
        return;
      }
      await toolStore.actions.updateOne(editTarget.value);
      state.editDialog = false;
    }


    // ============================================================
    // Delete Tag

    const deleteTarget = ref<RecipeTool | null>(null);

    function deleteEventHandler(item: RecipeTool) {
      state.deleteDialog = true;
      deleteTarget.value = item;
    }

    async function deleteTool() {
      if (!deleteTarget.value || deleteTarget.value.id === undefined) {
        return;
      }
      await toolStore.actions.deleteOne(deleteTarget.value.id);
      state.deleteDialog = false;
    }

    return {
      state,
      tableConfig,
      tableHeaders,
      tools: toolStore.items,
      validators,

      // create
      createTarget: toolData.data,
      createTool,

      // edit
      editTarget,
      editEventHandler,
      editSaveTool,

      // delete
      deleteTarget,
      deleteEventHandler,
      deleteTool
    };
  },
});
</script>
