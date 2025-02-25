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
          <v-checkbox v-model="createTarget.onHand" :label="$t('tool.on-hand')">
          </v-checkbox>
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
          <v-checkbox v-model="editTarget.onHand" :label="$t('tool.on-hand')"> </v-checkbox>
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
        <p v-if="deleteTarget" class="mt-4 ml-4">{{ deleteTarget.name }}</p>
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
    <BaseCardSectionTitle :icon="$globals.icons.potSteam" section :title="$tc('data-pages.tools.tool-data')"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="tools || []"
      :bulk-actions="[{icon: $globals.icons.delete, text: $tc('general.delete'), event: 'delete-selected'}]"
      initial-sort="name"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
      @delete-selected="bulkDeleteEventHandler"
    >
      <template #button-row>
        <BaseButton create @click="state.createDialog = true">{{ $t("general.create") }}</BaseButton>
      </template>
      <template #item.onHand="{ item }">
        <v-icon :color="item.onHand ? 'success' : undefined">
          {{ item.onHand ? $globals.icons.check : $globals.icons.close }}
        </v-icon>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, useContext } from "@nuxtjs/composition-api";
import { validators } from "~/composables/use-validators";
import { useToolStore, useToolData } from "~/composables/store";
import { RecipeTool } from "~/lib/api/types/recipe";

interface RecipeToolWithOnHand extends RecipeTool {
  onHand: boolean;
}

export default defineComponent({
  setup() {
    const { $auth, i18n } = useContext();
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
      {
        text: i18n.t("tool.on-hand"),
        value: "onHand",
        show: true,
      },
    ];

    const state = reactive({
      createDialog: false,
      editDialog: false,
      deleteDialog: false,
      bulkDeleteDialog: false,
    });

    const userHousehold = computed(() => $auth.user?.householdSlug || "");
    const toolData = useToolData();
    const toolStore = useToolStore();
    const tools = computed(() => toolStore.store.value.map((tools) => {
      const onHand = tools.householdsWithTool?.includes(userHousehold.value) || false;
      return { ...tools, onHand } as RecipeToolWithOnHand;
    }));


    // ============================================================
    // Create Tool

    async function createTool() {
      if (toolData.data.onHand) {
        toolData.data.householdsWithTool = [userHousehold.value];
      } else {
        toolData.data.householdsWithTool = [];
      }

      // @ts-ignore - only property really required is the name and onHand (RecipeOrganizerPage)
      await toolStore.actions.createOne({ name: toolData.data.name, householdsWithTool: toolData.data.householdsWithTool });
      toolData.reset();
      state.createDialog = false;
    }


    // ============================================================
    // Edit Tool

    const editTarget = ref<RecipeToolWithOnHand | null>(null);

    function editEventHandler(item: RecipeToolWithOnHand) {
      state.editDialog = true;
      editTarget.value = item;
    }

    async function editSaveTool() {
      if (!editTarget.value) {
        return;
      }
      if (editTarget.value.onHand && !editTarget.value.householdsWithTool?.includes(userHousehold.value)) {
        if (!editTarget.value.householdsWithTool) {
          editTarget.value.householdsWithTool = [userHousehold.value];
        } else {
          editTarget.value.householdsWithTool.push(userHousehold.value);
        }
      } else if (!editTarget.value.onHand && editTarget.value.householdsWithTool?.includes(userHousehold.value)) {
        editTarget.value.householdsWithTool = editTarget.value.householdsWithTool.filter(
          (household) => household !== userHousehold.value
        );
      }

      await toolStore.actions.updateOne(editTarget.value);
      state.editDialog = false;
    }


    // ============================================================
    // Delete Tool

    const deleteTarget = ref<RecipeToolWithOnHand | null>(null);

    function deleteEventHandler(item: RecipeToolWithOnHand) {
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

    // ============================================================
    // Bulk Delete Tool

    const bulkDeleteTarget = ref<RecipeToolWithOnHand[]>([]);
    function bulkDeleteEventHandler(selection: RecipeToolWithOnHand[]) {
      bulkDeleteTarget.value = selection;
      state.bulkDeleteDialog = true;
    }

    async function deleteSelected() {
      for (const item of bulkDeleteTarget.value) {
        await toolStore.actions.deleteOne(item.id);
      }
      bulkDeleteTarget.value = [];
    }

    return {
      state,
      tableConfig,
      tableHeaders,
      tools,
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
      deleteTool,

      // bulk delete
      bulkDeleteTarget,
      bulkDeleteEventHandler,
      deleteSelected,
    };
  },
});
</script>
