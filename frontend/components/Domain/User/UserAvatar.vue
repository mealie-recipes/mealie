<template>
  <v-list-item-avatar v-if="list && userId">
    <v-img :src="`/api/media/users/${userId}/profile.webp`" :alt="userId" @load="error = false" @error="error = true">
    </v-img>
  </v-list-item-avatar>
  <v-avatar v-else-if="userId" :size="size">
    <v-img :src="`/api/media/users/${userId}/profile.webp`" :alt="userId" @load="error = false" @error="error = true">
    </v-img>
  </v-avatar>
</template>

<script lang="ts">
import { defineComponent, toRefs, reactive } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    userId: {
      type: String,
      required: true,
    },
    list: {
      type: Boolean,
      default: false,
    },
    size: {
      type: String,
      default: "42",
    },
  },
  setup() {
    const state = reactive({
      error: false,
    });
    return {
      ...toRefs(state),
    };
  },
});
</script>