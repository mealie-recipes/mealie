<template>
  <v-container fluid>
    <BaseCardSectionTitle title="Manage Units"> </BaseCardSectionTitle>
    <v-toolbar flat color="background">
      <BaseDialog
        ref="domUnitDialog"
        :title="dialog.title"
        :icon="$globals.icons.units"
        :submit-text="dialog.text"
        :keep-open="!validForm"
        @submit="create ? actions.createOne(domCreateUnitForm) : actions.updateOne()"
      >
        <v-card-text>
          <v-form ref="domCreateUnitForm">
            <v-text-field v-model="workingUnitData.name" label="Name" :rules="[validators.required]"></v-text-field>
            <v-text-field v-model="workingUnitData.abbreviation" label="Abbreviation"></v-text-field>
            <v-text-field v-model="workingUnitData.description" label="Description"></v-text-field>
          </v-form>
        </v-card-text>
      </BaseDialog>

      <BaseButton
        class="mr-1"
        @click="
          create = true;
          actions.resetWorking();
          domUnitDialog.open();
        "
      ></BaseButton>
      <BaseButton secondary @click="filter = !filter"> Filter </BaseButton>
    </v-toolbar>

    <v-expand-transition>
      <div v-show="filter">
        <v-text-field v-model="search" style="max-width: 500px" label="Filter" class="ml-4"> </v-text-field>
      </div>
    </v-expand-transition>

    <v-data-table :headers="headers" :items="units || []" item-key="id" class="elevation-0" :search="search">
      <template #item.actions="{ item }">
        <div class="d-flex justify-end">
          <BaseButton
            edit
            small
            class="mr-2"
            @click="
              create = false;
              actions.setWorking(item);
              domUnitDialog.open();
            "
          ></BaseButton>
          <BaseDialog :title="$t('general.confirm')" color="error" @confirm="actions.deleteOne(item.id)">
            <template #activator="{ open }">
              <BaseButton delete small @click="open"></BaseButton>
            </template>
            <v-card-text>
              {{ $t("general.confirm-delete-generic") }}
            </v-card-text>
          </BaseDialog>
        </div>
      </template>
    </v-data-table>
    <v-divider></v-divider>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent, reactive, toRefs, ref, computed } from "@nuxtjs/composition-api";
import { useUnits } from "~/composables/use-recipe-units";
import { validators } from "~/composables/use-validators";
export default defineComponent({
  layout: "admin",
  setup() {
    const { units, actions, workingUnitData, validForm } = useUnits();

    const domCreateUnitForm = ref(null);
    const domUnitDialog = ref(null);

    const dialog = computed(() => {
      if (state.create) {
        return {
          title: "Create Unit",
          text: "Create",
        };
      } else {
        return {
          title: "Edit Unit",
          text: "Update",
        };
      }
    });

    const state = reactive({
      headers: [
        { text: "Id", value: "id" },
        { text: "Name", value: "name" },
        { text: "Abbreviation", value: "abbreviation" },
        { text: "Description", value: "description" },
        { text: "", value: "actions", sortable: false },
      ],
      filter: false,
      create: true,
      search: "",
    });

    return {
      ...toRefs(state),
      actions,
      dialog,
      domCreateUnitForm,
      domUnitDialog,
      units,
      validators,
      validForm,
      workingUnitData,
    };
  },
  head() {
    return {
      title: "Units",
    };
  },
});
</script>
    
<style scoped>
</style>