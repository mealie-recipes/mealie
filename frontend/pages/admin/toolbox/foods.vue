<template>
  <v-container fluid>
    <BaseCardSectionTitle title="Manage Units"> </BaseCardSectionTitle>
    <v-toolbar flat color="background">
      <!-- New/Edit Food Dialog -->
      <BaseDialog
        v-model="newFoodDialog"
        :title="dialog.title"
        :icon="$globals.icons.units"
        :submit-text="dialog.text"
        :keep-open="!validForm"
        @submit="create ? actions.createOne(domCreateFoodForm) : actions.updateOne()"
      >
        <v-card-text>
          <v-form ref="domCreateFoodForm">
            <v-text-field v-model="workingFoodData.name" label="Name" :rules="[validators.required]"></v-text-field>
            <v-text-field v-model="workingFoodData.description" label="Description"></v-text-field>
            <v-autocomplete
              v-model="workingFoodData.labelId"
              clearable
              :items="allLabels"
              item-value="id"
              item-text="name"
            >
            </v-autocomplete>
          </v-form>
        </v-card-text>
      </BaseDialog>

      <!-- Delete Food Dialog -->
      <BaseDialog
        v-model="deleteFoodDialog"
        :title="$t('general.confirm')"
        color="error"
        @confirm="actions.deleteOne(deleteTarget)"
      >
        <template #activator> </template>
        <v-card-text>
          {{ $t("general.confirm-delete-generic") }}
        </v-card-text>
      </BaseDialog>

      <BaseButton
        class="mr-1"
        @click="
          create = true;
          actions.resetWorking();
          newFoodDialog = true;
        "
      ></BaseButton>
      <BaseButton secondary @click="filter = !filter"> Filter </BaseButton>
    </v-toolbar>

    <v-expand-transition>
      <div v-show="filter">
        <v-text-field v-model="search" style="max-width: 500px" label="Filter" class="ml-4"> </v-text-field>
      </div>
    </v-expand-transition>

    <v-data-table :headers="headers" :items="foods || []" item-key="id" class="elevation-0" :search="search">
      <template #item.label="{ item }">
        <v-chip v-if="item.label" label>
          {{ item.label.name }}
        </v-chip>
      </template>
      <template #item.actions="{ item }">
        <div class="d-flex justify-end">
          <BaseButton
            edit
            small
            class="mr-2"
            @click="
              create = false;
              actions.setWorking(item);
              newFoodDialog = true;
            "
          ></BaseButton>
          <BaseButton
            delete
            small
            @click="
              deleteFoodDialog = true;
              deleteTarget = item.id;
            "
          ></BaseButton>
        </div>
      </template>
    </v-data-table>
    <v-divider></v-divider>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent, reactive, toRefs, ref, computed } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { useFoods } from "~/composables/recipes";
import { validators } from "~/composables/use-validators";
import { MultiPurposeLabelSummary } from "~/types/api-types/labels";
export default defineComponent({
  layout: "admin",
  setup() {
    const { foods, actions, workingFoodData, validForm } = useFoods();

    const domCreateFoodForm = ref(null);
    const domFoodDialog = ref(null);

    const dialog = computed(() => {
      if (state.create) {
        return {
          title: "Create Food",
          text: "Create",
        };
      } else {
        return {
          title: "Edit Food",
          text: "Update",
        };
      }
    });

    const state = reactive({
      deleteFoodDialog: false,
      newFoodDialog: false,
      deleteTarget: 0,
      headers: [
        { text: "Id", value: "id" },
        { text: "Name", value: "name" },
        { text: "Description", value: "description" },
        { text: "Label", value: "label" },
        { text: "", value: "actions", sortable: false },
      ],
      filter: false,
      create: true,
      search: "",
    });

    const userApi = useUserApi();

    const allLabels = ref([] as MultiPurposeLabelSummary[]);

    async function refreshLabels() {
      const { data } = await userApi.multiPurposeLabels.getAll();
      allLabels.value = data ?? [];
    }

    refreshLabels();

    return {
      allLabels,
      refreshLabels,
      ...toRefs(state),
      actions,
      dialog,
      domCreateFoodForm,
      domFoodDialog,
      foods,
      validators,
      validForm,
      workingFoodData,
    };
  },
  head() {
    return {
      title: "Foods",
    };
  },
});
</script>
    
<style scoped>
</style>