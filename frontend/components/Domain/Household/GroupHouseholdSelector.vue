<template>
  <v-select
    v-model="selected"
    :items="households"
    :label="label"
    :hint="description"
    :persistent-hint="!!description"
    item-title="name"
    :multiple="multiselect"
    :prepend-inner-icon="$globals.icons.household"
    return-object
  >
    <template #chip="data">
      <v-chip
        :key="data.index"
        class="ma-1"
        :input-value="data.item"
        size="small"
        closable
        label
        color="accent"
        dark
        @click:close="removeByIndex(data.index)"
      >
        {{ data.item.raw.name || data.item }}
      </v-chip>
    </template>
  </v-select>
</template>

<script lang="ts">
import { useHouseholdStore } from "~/composables/store/use-household-store";

interface HouseholdLike {
  id: string;
  name: string;
}

export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Array as () => HouseholdLike[],
      required: true,
    },
    multiselect: {
      type: Boolean,
      default: false,
    },
    description: {
      type: String,
      default: "",
    },
  },
  emits: ["update:modelValue"],
  setup(props, context) {
    const selected = computed({
      get: () => props.modelValue,
      set: (val) => {
        context.emit("update:modelValue", val);
      },
    });

    onMounted(() => {
      if (selected.value === undefined) {
        selected.value = [];
      }
    });

    const i18n = useI18n();
    const label = computed(
      () => props.multiselect ? i18n.t("household.households") : i18n.t("household.household"),
    );

    const { store: households } = useHouseholdStore();
    function removeByIndex(index: number) {
      if (selected.value === undefined) {
        return;
      }
      const newSelected = selected.value.filter((_, i) => i !== index);
      selected.value = [...newSelected];
    }

    return {
      selected,
      label,
      households,
      removeByIndex,
    };
  },
});
</script>
