<template>
  <div style="height: 100%;">
    <v-row class="my-0 mx-7">
      <v-spacer />
      <v-col class="text-right">
        <!-- Filters -->
        <v-menu
          offset-y
          bottom
          start
          nudge-bottom="3"
          :close-on-content-click="false"
        >
          <template #activator="{ props }">
            <v-badge
              :content="filterBadgeCount"
              :model-value="filterBadgeCount > 0"
              bordered
            >
              <v-btn
                class="rounded-circle"
                size="small"
                color="info"
                v-bind="props"
                icon
              >
                <v-icon> {{ $globals.icons.filter }} </v-icon>
              </v-btn>
            </v-badge>
          </template>
          <v-card>
            <v-list>
              <v-list-item
                :prepend-icon="preferences.orderDirection === 'asc' ? $globals.icons.sortCalendarDescending : $globals.icons.sortCalendarAscending"
                :title="preferences.orderDirection === 'asc' ? $t('general.sort-descending') : $t('general.sort-ascending')"
                @click="reverseSort"
              />
              <v-divider />
              <v-list-item
                v-for="option, idx in eventTypeFilterState"
                :key="idx"
              >
                <v-checkbox
                  :model-value="option.checked"
                  color="primary"
                  readonly
                  @click="toggleEventTypeOption(option.value)"
                >
                  <template #label>
                    <v-icon start>
                      {{ option.icon }}
                    </v-icon>
                    {{ option.label }}
                  </template>
                </v-checkbox>
              </v-list-item>
            </v-list>
          </v-card>
        </v-menu>
      </v-col>
    </v-row>
    <v-divider class="mx-2" />
    <div
      v-if="timelineEvents.length"
      id="timeline-container"
      height="fit-content"
      width="100%"
      class="px-1"
      :style="maxHeight ? `max-height: ${maxHeight}; overflow-y: auto;` : ''"
    >
      <v-timeline
        :density="$vuetify.display.smAndDown ? ($vuetify.display.xs ? 'compact' : 'comfortable') : undefined"
        justify="center"
        class="timeline"
      >
        <RecipeTimelineItem
          v-for="(event, index) in timelineEvents"
          :key="event.id"
          :event="event"
          :recipe="recipes.get(event.recipeId)"
          :show-recipe-cards="showRecipeCards"
          :width="$vuetify.display.smAndDown ? '100%' : undefined"
          @update="updateTimelineEvent(index)"
          @delete="deleteTimelineEvent(index)"
        />
      </v-timeline>
    </div>
    <v-card
      v-else-if="!loading"
      class="mt-2"
    >
      <v-card-title class="justify-center pa-9">
        {{ $t("recipe.timeline-no-events-found-try-adjusting-filters") }}
      </v-card-title>
    </v-card>
    <div
      v-if="loading"
      class="mb-3 text-center"
    >
      <AppLoader
        :loading="loading"
        :waiting-text="$t('general.loading-events')"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { useThrottleFn, whenever } from "@vueuse/core";
import RecipeTimelineItem from "./RecipeTimelineItem.vue";
import { useTimelinePreferences } from "~/composables/use-users/preferences";
import { useTimelineEventTypes } from "~/composables/recipes/use-recipe-timeline-events";
import { useAsyncKey } from "~/composables/use-utils";
import { alert } from "~/composables/use-toast";
import { useUserApi } from "~/composables/api";
import type { Recipe, RecipeTimelineEventOut, RecipeTimelineEventUpdate, TimelineEventType } from "~/lib/api/types/recipe";

export default defineNuxtComponent({
  components: { RecipeTimelineItem },

  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
    queryFilter: {
      type: String,
      required: true,
    },
    maxHeight: {
      type: [Number, String],
      default: undefined,
    },
    showRecipeCards: {
      type: Boolean,
      default: false,
    },
  },

  setup(props) {
    const api = useUserApi();
    const i18n = useI18n();
    const preferences = useTimelinePreferences();
    const { eventTypeOptions } = useTimelineEventTypes();
    const loading = ref(true);
    const ready = ref(false);

    const page = ref(1);
    const perPage = 32;
    const hasMore = ref(true);

    const timelineEvents = ref([] as RecipeTimelineEventOut[]);
    const recipes = new Map<string, Recipe>();
    const filterBadgeCount = computed(() => eventTypeOptions.value.length - preferences.value.types.length);
    const eventTypeFilterState = computed(() => {
      return eventTypeOptions.value.map((option) => {
        return {
          ...option,
          checked: preferences.value.types.includes(option.value),
        };
      });
    });

    interface ScrollEvent extends Event {
      target: HTMLInputElement;
    }

    const screenBuffer = 4;
    const onScroll = (event: ScrollEvent) => {
      if (!event.target) {
        return;
      }

      const { scrollTop, offsetHeight, scrollHeight } = event.target;

      // trigger when the user is getting close to the bottom
      const bottomOfElement = scrollTop + offsetHeight >= scrollHeight - (offsetHeight * screenBuffer);
      if (bottomOfElement) {
        infiniteScroll();
      }
    };

    whenever(
      () => props.modelValue,
      () => {
        initializeTimelineEvents();
      },
    );

    // Preferences
    function reverseSort() {
      if (loading.value) {
        return;
      }

      preferences.value.orderDirection = preferences.value.orderDirection === "asc" ? "desc" : "asc";
      initializeTimelineEvents();
    }

    function toggleEventTypeOption(option: TimelineEventType) {
      if (loading.value) {
        return;
      }

      const index = preferences.value.types.indexOf(option);
      if (index === -1) {
        preferences.value.types.push(option);
      }
      else {
        preferences.value.types.splice(index, 1);
      }

      initializeTimelineEvents();
    }

    // Timeline Actions
    async function updateTimelineEvent(index: number) {
      const event = timelineEvents.value[index];
      const payload: RecipeTimelineEventUpdate = {
        subject: event.subject,
        eventMessage: event.eventMessage,
        image: event.image,
      };

      const { response } = await api.recipes.updateTimelineEvent(event.id, payload);
      if (response?.status !== 200) {
        alert.error(i18n.t("events.something-went-wrong") as string);
        return;
      }

      alert.success(i18n.t("events.event-updated") as string);
    };

    async function deleteTimelineEvent(index: number) {
      const { response } = await api.recipes.deleteTimelineEvent(timelineEvents.value[index].id);
      if (response?.status !== 200) {
        alert.error(i18n.t("events.something-went-wrong") as string);
        return;
      }

      timelineEvents.value.splice(index, 1);
      alert.success(i18n.t("events.event-deleted") as string);
    };

    async function getRecipe(recipeId: string): Promise<Recipe | null> {
      const { data } = await api.recipes.getOne(recipeId);
      return data;
    };

    async function updateRecipes(events: RecipeTimelineEventOut[]) {
      const recipePromises: Promise<Recipe | null>[] = [];
      const seenRecipeIds: string[] = [];
      events.forEach((event) => {
        if (seenRecipeIds.includes(event.recipeId) || recipes.has(event.recipeId)) {
          return;
        }

        seenRecipeIds.push(event.recipeId);
        recipePromises.push(getRecipe(event.recipeId));
      });

      const results = await Promise.all(recipePromises);
      results.forEach((result) => {
        if (result && result.id) {
          recipes.set(result.id, result);
        }
      });
    }

    async function scrollTimelineEvents() {
      const orderBy = "timestamp";
      const orderDirection = preferences.value.orderDirection === "asc" ? "asc" : "desc";

      const eventTypeValue = `["${preferences.value.types.join("\", \"")}"]`;
      const queryFilter = `(${props.queryFilter}) AND eventType IN ${eventTypeValue}`;

      const response = await api.recipes.getAllTimelineEvents(page.value, perPage, { orderBy, orderDirection, queryFilter });
      page.value += 1;
      if (!response?.data) {
        return;
      }

      const events = response.data.items;
      if (events.length < perPage) {
        hasMore.value = false;
        if (!events.length) {
          return;
        }
      }

      // fetch recipes
      if (props.showRecipeCards) {
        await updateRecipes(events);
      }

      // this is set last so Vue knows to re-render
      timelineEvents.value.push(...events);
    };

    async function initializeTimelineEvents() {
      loading.value = true;
      ready.value = false;

      page.value = 1;
      hasMore.value = true;
      timelineEvents.value = [];
      await scrollTimelineEvents();

      ready.value = true;
      loading.value = false;
    }

    const infiniteScroll = useThrottleFn(() => {
      useAsyncData(useAsyncKey(), async () => {
        if (!hasMore.value || loading.value) {
          return;
        }

        loading.value = true;
        await scrollTimelineEvents();
        loading.value = false;
      });
    }, 500);

    // preload events
    initializeTimelineEvents();

    onMounted(
      () => {
        document.onscroll = () => {
          // if the inner element is scrollable, let its scroll event handle the infiniteScroll
          const timelineContainerElement = document.getElementById("timeline-container");
          if (timelineContainerElement) {
            const { clientHeight, scrollHeight } = timelineContainerElement;

            // if scrollHeight == clientHeight, the element is not scrollable, so we need to look at the global position
            // if scrollHeight > clientHeight, it is scrollable and we don't need to do anything here
            if (scrollHeight > clientHeight) {
              return;
            }
          }

          const bottomOfWindow = document.documentElement.scrollTop + window.innerHeight >= document.documentElement.offsetHeight - (window.innerHeight * screenBuffer);
          if (bottomOfWindow) {
            infiniteScroll();
          }
        };
      },
    );

    return {
      deleteTimelineEvent,
      filterBadgeCount,
      loading,
      onScroll,
      preferences,
      eventTypeFilterState,
      recipes,
      reverseSort,
      toggleEventTypeOption,
      timelineEvents,
      updateTimelineEvent,
    };
  },
});
</script>
