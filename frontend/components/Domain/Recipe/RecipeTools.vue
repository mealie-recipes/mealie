<template>
  <div v-if="edit || (value && value.length > 0)">
    <template v-if="edit">
      <v-autocomplete
        v-if="tools"
        v-model="recipeTools"
        :items="tools"
        item-text="name"
        multiple
        return-object
        deletable-chips
        :prepend-icon="$globals.icons.potSteam"
        chips
      >
        <template #selection="data">
          <v-chip
            :key="data.index"
            small
            class="ma-1"
            :input-value="data.selected"
            close
            label
            color="accent"
            dark
            @click:close="recipeTools.splice(data.index, 1)"
          >
            {{ data.item.name || data.item }}
          </v-chip>
        </template>
        <template #append-outer="">
          <BaseDialog v-model="createDialog" title="Create New Tool" @submit="actions.createOne()">
            <template #activator>
              <v-btn icon @click="createDialog = true">
                <v-icon> {{ $globals.icons.create }}</v-icon>
              </v-btn>
            </template>
            <v-card-text>
              <v-text-field v-model="workingToolData.name" label="Tool Name"></v-text-field>
              <v-checkbox v-model="workingToolData.onHand" label="Show as On Hand (Checked)"></v-checkbox>
            </v-card-text>
          </BaseDialog>
        </template>
      </v-autocomplete>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from "@nuxtjs/composition-api";
import { RecipeTool } from "~/types/api-types/recipe";
import { useTools } from "~/composables/recipes";

export default defineComponent({
  props: {
    value: {
      type: Array as () => RecipeTool[],
      required: true,
    },
    edit: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, context) {
    const { tools, actions, workingToolData } = useTools();

    const createDialog = ref(false);

    const recipeTools = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
      },
    });

    return {
      actions,
      createDialog,
      recipeTools,
      tools,
      workingToolData,
    };
  },
});
</script>

<style lang="scss" scoped>
</style>