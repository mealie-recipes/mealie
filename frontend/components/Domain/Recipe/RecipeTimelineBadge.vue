<template>
  <v-tooltip
    bottom
    nudge-right="50"
    :color="buttonStyle ? 'info' : 'secondary'"
  >
    <template #activator="{ props }">
      <v-btn
        icon
        :variant="buttonStyle ? 'flat' : undefined"
        :rounded="buttonStyle ? 'circle' : undefined"
        size="small"
        :color="buttonStyle ? 'info' : 'secondary'"
        :fab="buttonStyle"
        v-bind="{ ...props, ...$attrs }"
        @click.prevent="toggleTimeline"
      >
        <v-icon
          :size="!buttonStyle ? undefined : 'x-large'"
          :color="buttonStyle ? 'white' : 'secondary'"
        >
          {{ $globals.icons.timelineText }}
        </v-icon>
      </v-btn>
      <BaseDialog
        v-model="showTimeline"
        :title="timelineAttrs.title"
        :icon="$globals.icons.timelineText"
        width="70%"
      >
        <RecipeTimeline
          v-model="showTimeline"
          :query-filter="timelineAttrs.queryFilter"
          max-height="60vh"
        />
      </BaseDialog>
    </template>
    <span>{{ $t('recipe.open-timeline') }}</span>
  </v-tooltip>
</template>

<script lang="ts">
import RecipeTimeline from "./RecipeTimeline.vue";

export default defineNuxtComponent({
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
    const i18n = useI18n();
    const { smAndDown } = useDisplay();
    const showTimeline = ref(false);
    function toggleTimeline() {
      showTimeline.value = !showTimeline.value;
    }

    const timelineAttrs = computed(() => {
      let title = i18n.t("recipe.timeline");
      if (smAndDown.value) {
        title += ` – ${props.recipeName}`;
      }

      return {
        title,
        queryFilter: `recipe.slug="${props.slug}"`,
      };
    });

    return { showTimeline, timelineAttrs, toggleTimeline };
  },
});
</script>
