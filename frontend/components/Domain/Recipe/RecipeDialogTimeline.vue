<template>
    <BaseDialog
        v-model="dialog"
        title="Event Timeline"
        :icon="$globals.icons.timelineText"
      >
        <v-card-text>
          Placeholder. Coming soon!
        </v-card-text>
      </BaseDialog>
  </template>

  <script lang="ts">
  import { computed, defineComponent } from "@nuxtjs/composition-api";
  export default defineComponent({
    props: {
      value: {
        type: Boolean,
        default: false,
      },
      slug: {
        type: String,
        default: "",
      }
    },

    setup(props, context) {
      // V-Model Support
      const dialog = computed({
        get: () => {
          return props.value;
        },
        set: (val) => {
          console.log(val);
          context.emit("input", val);
        },
      });

      return {
        dialog
      };
    },
  });
  </script>
