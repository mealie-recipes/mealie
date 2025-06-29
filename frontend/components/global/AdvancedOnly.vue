<template>
  <div scoped-slot />
</template>

<script lang="ts">
/**
 * Renderless component that only renders if the user is logged in.
 * and has advanced options toggled.
 */
export default defineNuxtComponent({
  setup(_, ctx) {
    const $auth = useMealieAuth();

    const r = $auth.user.value?.advanced || false;

    return () => {
      return r ? ctx.slots.default?.() : null;
    };
  },
});
</script>
