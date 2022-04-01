<template>
  <div scoped-slot></div>
</template>

<script lang="ts">
import { defineComponent, useContext } from "@nuxtjs/composition-api";

/**
 * Renderless component that only renders if the user is logged in.
 * and has advanced options toggled.
 */
export default defineComponent({
  setup(_, ctx) {
    const { $auth } = useContext();

    const r = $auth?.user?.advanced || false;

    return () => {
      return r ? ctx.slots.default?.() : null;
    };
  },
});
</script>
