<template>
  <v-card flat class="pb-2">
    <h2 class="headline">{{ title }}</h2>
    <BaseDivider width="200px" color="primary" class="my-2" thickness="1px" />
    <p class="pb-0 mb-0">
      <slot />
    </p>
  </v-card>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: "Place Holder",
    },
  },
};
</script>
