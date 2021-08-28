<template>
  <BaseDialog
    title="Create Food"
    :icon="$globals.icons.foods"
    :keep-open="!validForm"
    @submit="actions.createOne(domCreateFoodForm)"
  >
    <v-card-text>
      <v-form ref="domCreateFoodForm">
        <v-text-field v-model="workingFoodData.name" label="Name" :rules="[validators.required]"></v-text-field>
        <v-text-field v-model="workingFoodData.description" label="Description"></v-text-field>
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
import { useFoods } from "~/composables/use-recipe-foods";
import { validators } from "~/composables/use-validators";
export default defineComponent({
  setup() {
    const domCreateFoodForm = ref(null);
    const { workingFoodData, actions, validForm } = useFoods();
    return { validators, workingFoodData, actions, domCreateFoodForm, validForm };
  },
});
</script>

