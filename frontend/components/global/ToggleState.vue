<template>
  <component :is="tag">
    <slot
      name="activator"
      v-bind="{ toggle, state }"
    />
    <slot v-bind="{ state, toggle }" />
  </component>
</template>

<script lang="ts">
export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
    tag: {
      type: String,
      default: "div",
    },
  },
  emits: ["update:modelValue"],
  setup(props, context) {
    const state = ref(false);

    const toggle = () => {
      state.value = !state.value;
    };

    watch(state, () => {
      context.emit("update:modelValue", state.value);
    });

    return {
      state,
      toggle,
    };
  },
});
</script>
