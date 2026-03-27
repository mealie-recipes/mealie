<template>
  <component :is="tag">
    <slot
      name="activator"
      v-bind="{ toggle, modelValue }"
    />
    <slot v-bind="{ modelValue, toggle }" />
  </component>
</template>

<script setup lang="ts">
const modelValue = defineModel({
  type: Boolean,
  default: false,
});

defineProps({
  tag: {
    type: String,
    default: "div",
  },
});

const toggle = () => {
  modelValue.value = !modelValue.value;
};
</script>
