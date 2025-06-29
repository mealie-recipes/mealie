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

<script lang="ts">
export default defineNuxtComponent({
  props: {
    link: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const href = computed(() => {
      // TODO: dynamically set docs link based off env
      return `https://nightly.mealie.io${props.link}`;
    });

    return { href };
  },
});
</script>
