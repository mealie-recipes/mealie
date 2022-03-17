<template>
  <div>
    <!-- Edit Dialog -->
    <BaseDialog
      v-model="editDialog"
      :icon="$globals.icons.units"
      title="Edit Food"
      :submit-text="$tc('general.save')"
      @submit="editSaveFood"
    >
      <v-card-text v-if="editTarget">
        <v-form ref="domCreateFoodForm">
          <v-text-field v-model="editTarget.name" label="Name" :rules="[validators.required]"></v-text-field>
          <v-text-field v-model="editTarget.abbreviation" label="Abbreviation"></v-text-field>
          <v-text-field v-model="editTarget.description" label="Description"></v-text-field>
          <v-checkbox v-model="editTarget.fraction" hide-details label="Display as Fraction"></v-checkbox>
        </v-form>
      </v-card-text>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="deleteDialog"
      :title="$tc('general.delete')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteFood"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <!-- Recipe Data Table -->
    <BaseCardSectionTitle :icon="$globals.icons.units" section title="Unit Data"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="units"
      :bulk-actions="[]"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
    >
      <template #item.fraction="{ item }">
        <v-icon :color="item.fraction ? 'success' : undefined">
          {{ item.fraction ? $globals.icons.check : $globals.icons.close }}
        </v-icon>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from "@nuxtjs/composition-api";
import { validators } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import { IngredientUnit } from "~/types/api-types/recipe";
import { MultiPurposeLabelSummary } from "~/types/api-types/labels";

export default defineComponent({
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
      {
        text: "Abbreviation",
        value: "abbreviation",
        show: true,
      },
      {
        text: "Description",
        value: "description",
        show: true,
      },
      {
        text: "Fraction",
        value: "fraction",
        show: true,
      },
    ];
    const units = ref<IngredientUnit[]>([]);
    async function refreshFoods() {
      const { data } = await userApi.units.getAll();
      units.value = data ?? [];
    }
    onMounted(() => {
      refreshFoods();
    });
    const editDialog = ref(false);
    const editTarget = ref<IngredientUnit | null>(null);
    function editEventHandler(item: IngredientUnit) {
      editTarget.value = item;
      editDialog.value = true;
    }
    async function editSaveFood() {
      if (!editTarget.value) {
        return;
      }

      const { data } = await userApi.units.updateOne(editTarget.value.id, editTarget.value);
      if (data) {
        refreshFoods();
      }

      editDialog.value = false;
    }
    const deleteDialog = ref(false);
    const deleteTarget = ref<IngredientUnit | null>(null);
    function deleteEventHandler(item: IngredientUnit) {
      deleteTarget.value = item;
      deleteDialog.value = true;
    }
    async function deleteFood() {
      if (!deleteTarget.value) {
        return;
      }

      const { data } = await userApi.units.deleteOne(deleteTarget.value.id);
      if (data) {
        refreshFoods();
      }
      deleteDialog.value = false;
    }

    // ============================================================
    // Labels

    const allLabels = ref([] as MultiPurposeLabelSummary[]);

    async function refreshLabels() {
      const { data } = await userApi.multiPurposeLabels.getAll();
      allLabels.value = data ?? [];
    }

    refreshLabels();
    return {
      tableConfig,
      tableHeaders,
      units,
      allLabels,
      validators,
      // Edit
      editDialog,
      editEventHandler,
      editSaveFood,
      editTarget,
      // Delete
      deleteEventHandler,
      deleteDialog,
      deleteFood,
    };
  },
});
</script>
