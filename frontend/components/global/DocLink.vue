<template>
  <v-btn x-small :href="href" color="primary" target="_blank">
    <v-icon left small>
      {{ $globals.icons.folderOutline }}
    </v-icon>
    {{ $tc("about.docs") }}
  </v-btn>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
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
