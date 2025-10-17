<template>
  <v-expansionPanels v-model="open">
    <slot />
  </v-expansionPanels>
</template>

<script lang="ts">
type DisclosureState = "closed" | "open";
export default defineComponent({
  props: {
    initialState: {
      type: () => String as unknown as DisclosureState,
      default: "closed",
    },
  },
  data() {
    return {
      open: ref(this.initialState === "open" ? 0 : undefined),
    };
  },
});
</script>
