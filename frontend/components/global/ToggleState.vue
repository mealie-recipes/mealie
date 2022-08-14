<template>
  <component :is="tag">
    <slot name="activator" v-bind="{ toggle, state }"> </slot>
    <slot v-bind="{ state, toggle }"></slot>
  </component>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    tag: {
      type: String,
      default: "div",
    },
  },
  setup(_, context) {
    const state = ref(false);

    const toggle = () => {
      state.value = !state.value;
    };

    watch(state, () => {
      context.emit("input", state);
    });

    return {
      state,
      toggle,
    };
  },
});
</script>
