<template>
  <div>
    <!-- Edit Dialog -->
    <BaseDialog
      v-model="editDialog"
      :icon="$globals.icons.foods"
      title="Edit Food"
      :submit-text="$tc('general.save')"
      @submit="editSaveFood"
    >
      <v-card-text v-if="editTarget">
        <v-form ref="domCreateFoodForm">
          <v-text-field v-model="editTarget.name" label="Name" :rules="[validators.required]"></v-text-field>
          <v-text-field v-model="editTarget.description" label="Description"></v-text-field>
          <v-autocomplete
            v-model="editTarget.labelId"
            clearable
            :items="allLabels"
            item-value="id"
            item-text="name"
            label="Food Label"
          >
          </v-autocomplete>
        </v-form> </v-card-text
    ></BaseDialog>

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
    <BaseCardSectionTitle :icon="$globals.icons.foods" section title="Food Data"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="foods"
      :bulk-actions="[]"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
    >
      <template #button-row>
        <BaseButton :disabled="true">
          <template #icon> {{ $globals.icons.foods }} </template>
          Combine
        </BaseButton>
      </template>
      <template #item.label="{ item }">
        <MultiPurposeLabel v-if="item.label" :label="item.label">
          {{ item.label.name }}
        </MultiPurposeLabel>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from "@nuxtjs/composition-api";
import { validators } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import { IngredientFood } from "~/types/api-types/recipe";
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
      {
        text: "Description",
        value: "description",
        show: true,
      },
      {
        text: "Label",
        value: "label",
        show: true,
      },
    ];
    const foods = ref<IngredientFood[]>([]);
    async function refreshFoods() {
      const { data } = await userApi.foods.getAll();
      foods.value = data ?? [];
    }
    onMounted(() => {
      refreshFoods();
    });
    const editDialog = ref(false);
    const editTarget = ref<IngredientFood | null>(null);
    function editEventHandler(item: IngredientFood) {
      editTarget.value = item;
      editDialog.value = true;
    }
    async function editSaveFood() {
      if (!editTarget.value) {
        return;
      }

      const { data } = await userApi.foods.updateOne(editTarget.value.id, editTarget.value);
      if (data) {
        refreshFoods();
      }

      editDialog.value = false;
    }
    const deleteDialog = ref(false);
    const deleteTarget = ref<IngredientFood | null>(null);
    function deleteEventHandler(item: IngredientFood) {
      deleteTarget.value = item;
      deleteDialog.value = true;
    }
    async function deleteFood() {
      if (!deleteTarget.value) {
        return;
      }

      const { data } = await userApi.foods.deleteOne(deleteTarget.value.id);
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
      foods,
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
