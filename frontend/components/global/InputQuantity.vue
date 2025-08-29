<template>
  <div
    class="d-flex align-center"
    style="max-width: 60px"
  >
    <v-text-field
      v-model.number="quantity"
      hide-details
      :label="$t('form.quantity-label-abbreviated')"
      :min="min"
      :max="max"
      type="number"
      variant="plain"
      density="compact"
      style="width: 60px;"
    />
  </div>
</template>

<script lang="ts">
export default defineNuxtComponent({
  name: "VInputNumber",
  props: {
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
    modelValue: {
      type: Number,
      default: 0,
    },
  },
  emits: ["update:modelValue"],
  setup(props, context) {
    const quantity = computed({
      get: () => {
        return Number(props.modelValue);
      },
      set: (val) => {
        context.emit("update:modelValue", val);
      },
    });

    return {
      quantity,
    };
  },
});
</script>
