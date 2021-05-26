<template>
  <v-progress-circular class="mx-auto" :width="size / 20" :size="size" color="primary lighten-2" indeterminate>
    <div class="text-center">
      <v-icon :size="size / 2" color="primary lighten-2">
        {{ $globals.icons.primary }}
      </v-icon>
      <div>
        Loading Recipes
      </div>
    </div>
  </v-progress-circular>
</template>

<script>
export default {
  props: {
    loading: {
      default: true,
    },
    size: {
      default: 200,
    },
  },
};
</script>
