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
      <BaseDialog v-model="showTimeline" :title="timelineAttrs.title" :icon="$globals.icons.timelineText" width="70%">
        <RecipeTimeline v-model="showTimeline" :query-filter="timelineAttrs.queryFilter" max-height="60vh" />
      </BaseDialog>

    </template>
    <span>{{ $t('recipe.open-timeline') }}</span>
  </v-tooltip>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import RecipeTimeline from "./RecipeTimeline.vue";
export default defineComponent({
  components: { RecipeTimeline },

  props: {
    buttonStyle: {
      type: Boolean,
      default: false,
    },
    slug: {
      type: String,
      default: "",
    },
    recipeName: {
      type: String,
      default: "",
    },
  },

  setup(props) {
    const { $vuetify, i18n } = useContext();
    const showTimeline = ref(false);
    function toggleTimeline() {
      showTimeline.value = !showTimeline.value;
    }

    const timelineAttrs = computed(() => {
      let title = i18n.tc("recipe.timeline")
      if ($vuetify.breakpoint.smAndDown) {
        title += ` – ${props.recipeName}`
      }

      return {
        title,
        queryFilter: `recipe.slug="${props.slug}"`,
      }
    })

    return { showTimeline, timelineAttrs, toggleTimeline };
  },
});
</script>
