<template>
  <div class="mt-4">
    <section class="d-flex flex-column align-center">
      <slot name="header"></slot>
      <h2 class="headline">
        <slot name="title"> 👋 Here's a Title </slot>
      </h2>

      <h3 class="subtitle-1">
        <slot> </slot>
      </h3>
    </section>
    <section class="d-flex">
      <slot name="content"></slot>
    </section>
    <v-divider v-if="divider" class="my-4"></v-divider>
  </div>
</template>

<script>
export default {
  props: {
    divider: {
      type: Boolean,
      default: false,
    },
  },
};
</script>