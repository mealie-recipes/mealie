<template>
  <div class="d-flex align-center" style="max-width: 60px">
    <v-text-field
      v-model.number="quantity"
      hide-details
      label="Qty"
      :min="min"
      :max="max"
      type="number"
      class="rounded-xl"
      small
      text
    >
    </v-text-field>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  name: "VInputNumber",
  props: {
    label: {
      type: String,
      default: "Qty",
    },
    min: {
      type: Number,
      default: 0,
    },
    max: {
      type: Number,
      default: 9999,
    },
    rules: {
      type: Array,
      default: () => [],
    },
    step: {
      type: Number,
      default: 1,
    },
    value: {
      type: Number,
      default: 0,
    },
  },
  setup(props, context) {
    const quantity = computed({
      get: () => {
        return Number(props.value);
      },
      set: (val) => {
        context.emit("input", val);
      },
    });

    return {
      quantity,
    };
  },
});
</script>