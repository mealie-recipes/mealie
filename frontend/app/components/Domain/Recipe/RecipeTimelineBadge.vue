<template>
  <v-tooltip
    location="bottom"
    nudge-right="50"
    :color="buttonStyle ? 'info' : 'secondary'"
  >
    <template #activator="{ props: activatorProps }">
      <button
        v-if="pill"
        type="button"
        class="mealie-pill mealie-pill--sm mealie-pill--icon"
        :aria-label="$t('recipe.open-timeline')"
        v-bind="{ ...activatorProps, ...$attrs }"
        @click.prevent="toggleTimeline"
      >
        <v-icon size="16">
          {{ $globals.icons.timelineText }}
        </v-icon>
      </button>
      <v-btn
        v-else
        icon
        :variant="buttonStyle ? 'flat' : undefined"
        :rounded="buttonStyle ? 'circle' : undefined"
        size="small"
        :color="buttonStyle ? 'info' : 'secondary'"
        :fab="buttonStyle"
        v-bind="{ ...activatorProps, ...$attrs }"
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
        :title="$t('recipe.timeline')"
        :icon="$globals.icons.timelineText"
        width="70%"
      >
        <RecipeTimeline
          v-model="showTimeline"
          :query-filter="timelineAttrs.queryFilter"
        />
      </BaseDialog>
    </template>
    <span>{{ $t('recipe.open-timeline') }}</span>
  </v-tooltip>
</template>

<script setup lang="ts">
import RecipeTimeline from "./RecipeTimeline.vue";

interface Props {
  buttonStyle?: boolean;
  /** a small neutral pill, for the recipe page toolbar */
  pill?: boolean;
  slug?: string;
  recipeName?: string;
}
const props = withDefaults(defineProps<Props>(), {
  buttonStyle: false,
  pill: false,
  slug: "",
  recipeName: "",
});

const showTimeline = ref(false);

function toggleTimeline() {
  showTimeline.value = !showTimeline.value;
}

const timelineAttrs = computed(() => {
  return {
    queryFilter: `recipe.slug="${props.slug}"`,
  };
});
</script>
