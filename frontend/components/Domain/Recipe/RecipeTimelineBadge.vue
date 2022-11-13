<template>
    <v-tooltip bottom nudge-right="50" :color="buttonStyle ? 'info' : 'secondary'">
      <template #activator="{ on, attrs }">
        <v-btn
          small
          :color="buttonStyle ? 'info' : 'secondary'"
          :fab="buttonStyle"
          class="ml-1"
          v-bind="attrs"
          v-on="on"
          @click.prevent="toggleTimeline"
        >
          <v-icon :small="!buttonStyle" :color="buttonStyle ? 'white' : 'secondary'">
            {{ $globals.icons.timelineText }}
          </v-icon>
        </v-btn>
        <RecipeDialogTimeline v-model="showTimeline" :slug=slug />
      </template>
      <span>Open Event Timeline</span>
    </v-tooltip>
  </template>

  <script lang="ts">
  import { defineComponent, ref } from "@nuxtjs/composition-api";
  import RecipeDialogTimeline from "./RecipeDialogTimeline.vue";
  export default defineComponent({
    components: { RecipeDialogTimeline },

    props: {
      slug: {
        type: String,
        default: "",
      },
      buttonStyle: {
        type: Boolean,
        default: false,
      },
    },

    setup() {
      const showTimeline = ref(false);
      function toggleTimeline() {
        showTimeline.value = !showTimeline.value;
      }

      return { showTimeline, toggleTimeline };
    },
  });
  </script>
