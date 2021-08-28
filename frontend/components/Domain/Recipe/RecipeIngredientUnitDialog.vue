<template>
  <BaseDialog
    title="Create Unit"
    :icon="$globals.icons.units"
    :keep-open="!validForm"
    @submit="actions.createOne(domCreateUnitForm)"
  >
    <v-card-text>
      <v-form ref="domCreateUnitForm">
        <v-text-field v-model="workingUnitData.name" label="Name" :rules="[validators.required]"></v-text-field>
        <v-text-field v-model="workingUnitData.abbreviation" label="Abbreviation"></v-text-field>
        <v-text-field v-model="workingUnitData.description" label="Description"></v-text-field>
        <v-switch v-model="workingUnitData.fraction" label="Display as Fraction"></v-switch>
      </v-form>
    </v-card-text>
    <template #activator="{ open }">
      <BaseButton
        v-bind="$attrs"
        @click="
          actions.resetWorking();
          open();
        "
      ></BaseButton>
    </template>
  </BaseDialog>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { useUnits } from "~/composables/use-recipe-units";
import { validators } from "~/composables/use-validators";
export default defineComponent({
  setup() {
    const domCreateUnitForm = ref(null);
    const { workingUnitData, actions, validForm } = useUnits();
    return { validators, workingUnitData, actions, validForm, domCreateUnitForm };
  },
});
</script>

