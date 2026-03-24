<template>
  <v-tooltip
    location="bottom"
    nudge-right="50"
    :color="buttonStyle ? 'info' : 'secondary'"
  >
    <template #activator="{ props: activatorProps }">
      <v-btn
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
        :title="timelineAttrs.title"
        :icon="$globals.icons.timelineText"
        width="70%"
      >
        <v-tabs v-model="activeTab" density="compact" class="mb-2">
          <v-tab value="timeline">
            {{ $t('recipe.timeline') }}
          </v-tab>
          <v-tab value="versions">
            {{ $t('recipe.version-history') }}
          </v-tab>
        </v-tabs>

        <v-tabs-window v-model="activeTab">
          <v-tabs-window-item value="timeline">
            <RecipeTimeline
              v-model="showTimeline"
              :query-filter="timelineAttrs.queryFilter"
              max-height="60vh"
            />
          </v-tabs-window-item>
          <v-tabs-window-item value="versions">
            <RecipeVersionHistory
              v-if="slug"
              :slug="slug"
              :can-edit="true"
              inline
              @restored="showTimeline = false"
            />
          </v-tabs-window-item>
        </v-tabs-window>
      </BaseDialog>
    </template>
    <span>{{ $t('recipe.open-timeline') }}</span>
  </v-tooltip>
</template>

<script setup lang="ts">
import RecipeTimeline from "./RecipeTimeline.vue";
import RecipeVersionHistory from "./RecipeVersionHistory.vue";

interface Props {
  buttonStyle?: boolean;
  slug?: string;
  recipeName?: string;
}
const props = withDefaults(defineProps<Props>(), {
  buttonStyle: false,
  slug: "",
  recipeName: "",
});

const i18n = useI18n();
const { smAndDown } = useDisplay();
const showTimeline = ref(false);
const activeTab = ref("timeline");

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
</script>
