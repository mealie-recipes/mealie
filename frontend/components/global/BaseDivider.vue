<template>
  <v-divider :width="width" class="mx-auto" :class="color" :style="`border-width: ${thickness} !important`" />
</template>

<script>
export default {
  props: {
    width: {
      type: String,
      default: "100px"
    },
    thickness: {
      type: String,
      default: "2px"
    },
    color: {
      type: String,
      default: "accent"
    }
  }
}
</script>
