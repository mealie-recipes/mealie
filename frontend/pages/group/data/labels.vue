<template>
  <div>
    <!-- Create New Dialog -->
    <BaseDialog v-model="state.createDialog" title="New Label" :icon="$globals.icons.tags" @submit="createLabel">
      <v-card-text>
        <MultiPurposeLabel :label="createLabelData" />

        <div class="mt-4">
          <v-text-field v-model="createLabelData.name" :label="$t('general.name')"> </v-text-field>
          <InputColor v-model="createLabelData.color" />
        </div>
      </v-card-text>
    </BaseDialog>

    <!-- Edit Dialog -->
    <BaseDialog
      v-model="state.editDialog"
      :icon="$globals.icons.tags"
      title="Edit Label"
      :submit-text="$tc('general.save')"
      @submit="editSaveLabel"
    >
      <v-card-text v-if="editLabel">
        <MultiPurposeLabel :label="editLabel" />
        <div class="mt-4">
          <v-text-field v-model="editLabel.name" :label="$t('general.name')"> </v-text-field>
          <InputColor v-model="editLabel.color" />
        </div>
      </v-card-text>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="state.deleteDialog"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteLabel"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <!-- Recipe Data Table -->
    <BaseCardSectionTitle :icon="$globals.icons.tags" section title="Labels"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="labels"
      :bulk-actions="[]"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
    >
      <template #button-row>
        <BaseButton create @click="state.createDialog = true">
          <template #icon> {{ $globals.icons.tags }} </template>
          Create
        </BaseButton>
      </template>
      <template #item.name="{ item }">
        <MultiPurposeLabel v-if="item" :label="item">
          {{ item.name }}
        </MultiPurposeLabel>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref } from "@nuxtjs/composition-api";
import { validators } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import MultiPurposeLabel from "~/components/Domain/ShoppingList/MultiPurposeLabel.vue";
import { MultiPurposeLabelSummary } from "~/types/api-types/labels";

export default defineComponent({
  components: { MultiPurposeLabel },
  setup() {
    const userApi = useUserApi();
    const tableConfig = {
      hideColumns: true,
      canExport: true,
    };
    const tableHeaders = [
      {
        text: "Id",
        value: "id",
        show: false,
      },
      {
        text: "Name",
        value: "name",
        show: true,
      },
    ];

    const state = reactive({
      createDialog: false,
      editDialog: false,
      deleteDialog: false,
    });

    // ============================================================
    // Labels

    const labels = ref([] as MultiPurposeLabelSummary[]);

    async function refreshLabels() {
      const { data } = await userApi.multiPurposeLabels.getAll();
      labels.value = data ?? [];
    }

    // Create

    const createLabelData = ref({
      groupId: "",
      id: "",
      name: "",
      color: "",
    });

    async function createLabel() {
      await userApi.multiPurposeLabels.createOne(createLabelData.value);
      createLabelData.value = {
        groupId: "",
        id: "",
        name: "",
        color: "",
      };
      refreshLabels();
      state.createDialog = false;
    }

    // Delete

    const deleteTarget = ref<MultiPurposeLabelSummary | null>(null);

    function deleteEventHandler(item: MultiPurposeLabelSummary) {
      state.deleteDialog = true;
      deleteTarget.value = item;
    }

    async function deleteLabel() {
      if (!deleteTarget.value) {
        return;
      }
      const { data } = await userApi.multiPurposeLabels.deleteOne(deleteTarget.value.id);
      if (data) {
        refreshLabels();
      }
      state.deleteDialog = false;
    }

    // Edit

    const editLabel = ref<MultiPurposeLabelSummary | null>(null);

    function editEventHandler(item: MultiPurposeLabelSummary) {
      state.editDialog = true;
      editLabel.value = item;

      if (!editLabel.value.color) {
        editLabel.value.color = "#E0E0E0";
      }
    }

    async function editSaveLabel() {
      if (!editLabel.value) {
        return;
      }
      const { data } = await userApi.multiPurposeLabels.updateOne(editLabel.value.id, editLabel.value);
      if (data) {
        refreshLabels();
      }
      state.editDialog = false;
    }

    refreshLabels();

    return {
      state,
      tableConfig,
      tableHeaders,
      labels,
      validators,

      deleteEventHandler,
      deleteLabel,
      editLabel,
      editEventHandler,
      editSaveLabel,
      createLabel,
      createLabelData,
    };
  },
});
</script>
