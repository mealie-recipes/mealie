<template>
  <v-toolbar
    color="transparent"
    flat
  >
    <BaseButton
      color="null"
      rounded
      secondary
      @click="$router.go(-1)"
    >
      <template #icon>
        {{ $globals.icons.arrowLeftBold }}
      </template>
      {{ $t('general.back') }}
    </BaseButton>
    <slot />
  </v-toolbar>
</template>

<script lang="ts">
export default defineNuxtComponent({
  props: {
    back: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style lang="scss" scoped>
</style>
