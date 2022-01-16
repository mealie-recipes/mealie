<template>
  <div>
    <v-btn outlined class="rounded-xl my-1 mx-1" :to="to">
      <v-icon v-if="icon != ''" left>
        {{ icon }}
      </v-icon>
      {{ text }}
    </v-btn>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    to: {
      type: String,
      required: true,
    },
    text: {
      type: String,
      default: "Link",
    },
    icon: {
      type: String,
      default: "",
    },
  },
});
</script>