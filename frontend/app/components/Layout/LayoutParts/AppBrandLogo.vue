<template>
  <!-- decorative: it always sits next to the "Mealie" name -->
  <img
    v-if="logoUrl"
    :src="logoUrl"
    alt=""
    class="app-logo"
    :width="size"
    :height="size"
  >
  <v-icon
    v-else
    :size="size"
    color="primary"
    class="app-logo"
    aria-hidden="true"
  >
    {{ $globals.icons.primary }}
  </v-icon>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 28 });

const { brandingUrl } = useBranding();
const logoUrl = brandingUrl("logo.png");
</script>

<style scoped>
.app-logo {
  flex-shrink: 0;
  object-fit: contain;
}
</style>
