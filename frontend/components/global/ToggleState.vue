<template>
  <component :is="tag">
    <slot name="activator" v-bind="{ toggle, state }"> </slot>
    <slot v-bind="{ state, toggle }"></slot>
  </component>
</template>
    
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { useToggle } from "@vueuse/shared";

export default defineComponent({
  props: {
    tag: {
      type: String,
      default: "div",
    },
  },
  setup() {
    const [state, toggle] = useToggle();
    console.log(state, toggle);
    return {
      state,
      toggle,
    };
  },
});
</script>
    