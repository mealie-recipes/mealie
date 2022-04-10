<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog v-model="mergeDialog" :icon="$globals.icons.foods" title="Combine Food" @confirm="mergeFoods">
      <v-card-text>
        Combining the selected foods will merge the Source Food and Target Food into a single food. The
        <strong> Source Food will be deleted </strong> and all of the references to the Source Food will be updated to
        point to the Target Food.
        <v-autocomplete v-model="fromFood" return-object :items="foods" item-text="name" label="Source Food" />
        <v-autocomplete v-model="toFood" return-object :items="foods" item-text="name" label="Target Food" />

        <template v-if="canMerge && fromFood && toFood">
          <div class="text-center">Merging {{ fromFood.name }} into {{ toFood.name }}</div>
        </template>
      </v-card-text>
    </BaseDialog>

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
      :title="$tc('general.confirm')"
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
        <BaseButton @click="mergeDialog = true">
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
import { computed } from "vue-demi";
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
    // Merge Foods

    const mergeDialog = ref(false);
    const fromFood = ref<IngredientFood | null>(null);
    const toFood = ref<IngredientFood | null>(null);

    const canMerge = computed(() => {
      return fromFood.value && toFood.value && fromFood.value.id !== toFood.value.id;
    });

    async function mergeFoods() {
      if (!canMerge.value || !fromFood.value || !toFood.value) {
        return;
      }

      const { data } = await userApi.foods.merge(fromFood.value.id, toFood.value.id);

      if (data) {
        refreshFoods();
      }
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
      // Merge
      canMerge,
      mergeFoods,
      mergeDialog,
      fromFood,
      toFood,
    };
  },
});
</script>
