<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog v-model="mergeDialog" :icon="$globals.icons.units" title="Combine Unit" @confirm="mergeUnits">
      <v-card-text>
        Combining the selected units will merge the Source Unit and Target Unit into a single unit. The
        <strong> Source Unit will be deleted </strong> and all of the references to the Source Unit will be updated to
        point to the Target Unit.
        <v-autocomplete v-model="fromUnit" return-object :items="units" item-text="name" label="Source Unit" />
        <v-autocomplete v-model="toUnit" return-object :items="units" item-text="name" label="Target Unit" />

        <template v-if="canMerge && fromUnit && toUnit">
          <div class="text-center">Merging {{ fromUnit.name }} into {{ toUnit.name }}</div>
        </template>
      </v-card-text>
    </BaseDialog>

    <!-- Edit Dialog -->
    <BaseDialog
      v-model="editDialog"
      :icon="$globals.icons.units"
      title="Edit Unit"
      :submit-text="$tc('general.save')"
      @submit="editSaveUnit"
    >
      <v-card-text v-if="editTarget">
        <v-form ref="domCreateUnitForm">
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
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteUnit"
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
      <template #button-row>
        <BaseButton @click="mergeDialog = true">
          <template #icon> {{ $globals.icons.units }} </template>
          Combine
        </BaseButton>
      </template>
      <template #item.fraction="{ item }">
        <v-icon :color="item.fraction ? 'success' : undefined">
          {{ item.fraction ? $globals.icons.check : $globals.icons.close }}
        </v-icon>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, ref } from "@nuxtjs/composition-api";
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
    async function refreshUnits() {
      const { data } = await userApi.units.getAll();
      units.value = data ?? [];
    }
    onMounted(() => {
      refreshUnits();
    });
    const editDialog = ref(false);
    const editTarget = ref<IngredientUnit | null>(null);
    function editEventHandler(item: IngredientUnit) {
      editTarget.value = item;
      editDialog.value = true;
    }
    async function editSaveUnit() {
      if (!editTarget.value) {
        return;
      }

      const { data } = await userApi.units.updateOne(editTarget.value.id, editTarget.value);
      if (data) {
        refreshUnits();
      }

      editDialog.value = false;
    }
    const deleteDialog = ref(false);
    const deleteTarget = ref<IngredientUnit | null>(null);
    function deleteEventHandler(item: IngredientUnit) {
      deleteTarget.value = item;
      deleteDialog.value = true;
    }
    async function deleteUnit() {
      if (!deleteTarget.value) {
        return;
      }

      const { data } = await userApi.units.deleteOne(deleteTarget.value.id);
      if (data) {
        refreshUnits();
      }
      deleteDialog.value = false;
    }

    // ============================================================
    // Merge Units

    const mergeDialog = ref(false);
    const fromUnit = ref<IngredientUnit | null>(null);
    const toUnit = ref<IngredientUnit | null>(null);

    const canMerge = computed(() => {
      return fromUnit.value && toUnit.value && fromUnit.value.id !== toUnit.value.id;
    });

    async function mergeUnits() {
      if (!canMerge.value || !fromUnit.value || !toUnit.value) {
        return;
      }

      const { data } = await userApi.units.merge(fromUnit.value.id, toUnit.value.id);

      if (data) {
        refreshUnits();
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
      units,
      allLabels,
      validators,
      // Edit
      editDialog,
      editEventHandler,
      editSaveUnit,
      editTarget,
      // Delete
      deleteEventHandler,
      deleteDialog,
      deleteUnit,
      // Merge
      canMerge,
      mergeUnits,
      mergeDialog,
      fromUnit,
      toUnit,
    };
  },
});
</script>
