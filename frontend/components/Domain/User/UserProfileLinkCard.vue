<template>
  <v-card outlined nuxt :to="link.to" height="100%" class="d-flex flex-column">
    <div v-if="$vuetify.breakpoint.smAndDown" class="pa-2 mx-auto">
      <v-img max-width="150px" max-height="125" :src="image"></v-img>
    </div>
    <div class="d-flex align-center justify-space-between">
      <div>
        <v-card-title class="headline pb-0">
          <slot name="title"> </slot>
        </v-card-title>
        <div class="d-flex justify-center align-center">
          <v-card-text class="d-flex flex-row mb-auto">
            <slot name="default"></slot>
          </v-card-text>
        </div>
      </div>
      <div v-if="$vuetify.breakpoint.mdAndUp" class="px-10">
        <v-img max-width="150px" max-height="125" :src="image"></v-img>
      </div>
    </div>
    <v-divider class="mt-auto"></v-divider>
    <v-card-actions>
      <v-btn text color="info" :to="link.to">
        {{ link.text }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

interface LinkProp {
  text: string;
  url?: string;
  to: string;
}

export default defineComponent({
  props: {
    link: {
      type: Object as () => LinkProp,
      required: true,
    },
    image: {
      type: String,
      requried: false,
      default: "",
    },
  },
  setup() {
    return {};
  },
});
</script>
    
