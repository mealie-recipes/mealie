<template>
  <v-btn
    size="x-small"
    :href="href"
    color="primary"
    target="_blank"
  >
    <v-icon
      start
      size="small"
    >
      {{ $globals.icons.folderOutline }}
    </v-icon>
    {{ $t("about.docs") }}
  </v-btn>
</template>

<script setup lang="ts">
const props = defineProps({
  link: {
    type: String,
    required: true,
  },
});

const href = computed(() => {
  // TODO: dynamically set docs link based off env
  return `https://docs.mealie.io${props.link}`;
});
</script>
