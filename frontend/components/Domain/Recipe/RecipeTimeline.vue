<template>
  <div :style="maxHeight ? `max-height: ${maxHeight}; overflow-y: auto;` : ''" @scroll="onScroll($event)">
    <v-row class="my-0 mx-7">
      <v-spacer />
      <v-col class="text-right">
        <v-btn fab small color="info" @click="reverseSort">
          <v-icon> {{ preferences.orderDirection === "asc" ? $globals.icons.sortCalendarAscending : $globals.icons.sortCalendarDescending }} </v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-divider v-if="timelineEvents.length" />
    <v-card
      v-if="timelineEvents.length"
      id="timeline-container"
      height="fit-content"
      width="100%"
      class="px-1"
    >
      <v-timeline :dense="$vuetify.breakpoint.smAndDown" class="timeline">
        <RecipeTimelineItem
          v-for="(event, index) in timelineEvents"
          :key="event.id"
          :event="event"
          :recipe="recipes.get(event.recipeId)"
          :show-recipe-cards="showRecipeCards"
          @update="updateTimelineEvent(index)"
          @delete="deleteTimelineEvent(index)"
        />
      </v-timeline>
    </v-card>
    <v-card v-else-if="!loading">
      <v-card-title class="justify-center pa-9">
        {{ $t("recipe.timeline-is-empty") }}
      </v-card-title>
    </v-card>
    <div v-if="loading" class="pb-3">
      <AppLoader :loading="loading" :waiting-text="$tc('general.loading-events')" />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, useAsync, useContext } from "@nuxtjs/composition-api";
import { useThrottleFn, whenever } from "@vueuse/core";
import RecipeTimelineItem from "./RecipeTimelineItem.vue"
import { useTimelinePreferences } from "~/composables/use-users/preferences";
import { useAsyncKey } from "~/composables/use-utils";
import { alert } from "~/composables/use-toast";
import { useUserApi } from "~/composables/api";
import { Recipe, RecipeTimelineEventOut, RecipeTimelineEventUpdate } from "~/lib/api/types/recipe"

export default defineComponent({
  components: { RecipeTimelineItem },

  props: {
    value: {
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
    }
  },

  setup(props) {
    const api = useUserApi();
    const { i18n } = useContext();
    const preferences = useTimelinePreferences();
    const loading = ref(true);
    const ready = ref(false);

    const page = ref(1);
    const perPage = 32;
    const hasMore = ref(true);

    const timelineEvents = ref([] as RecipeTimelineEventOut[]);
    const recipes = new Map<string, Recipe>();

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
      const bottomOfElement = scrollTop + offsetHeight >= scrollHeight - (offsetHeight*screenBuffer);
      if (bottomOfElement) {
        infiniteScroll();
      }
    };

    document.onscroll = () => {
      // if the inner element is scrollable, let its scroll event handle the infiniteScroll
      const timelineContainerElement = document.getElementById("timeline-container");
      if (timelineContainerElement) {
        const { clientHeight, scrollHeight } = timelineContainerElement

        // if scrollHeight == clientHeight, the element is not scrollable, so we need to look at the global position
        // if scrollHeight > clientHeight, it is scrollable and we don't need to do anything here
        if (scrollHeight > clientHeight) {
          return;
        }
      }

      const bottomOfWindow = document.documentElement.scrollTop + window.innerHeight >= document.documentElement.offsetHeight - (window.innerHeight*screenBuffer);
      if (bottomOfWindow) {
        infiniteScroll();
      }
    };

    whenever(
      () => props.value,
      () => {
        if (!ready.value) {
          initializeTimelineEvents();
        }
      }
    );

    // Sorting
    function reverseSort() {
      if (loading.value) {
        return;
      }

      preferences.value.orderDirection = preferences.value.orderDirection === "asc" ?  "desc" : "asc";
      initializeTimelineEvents();
    }

    // Timeline Actions
    async function updateTimelineEvent(index: number) {
      const event = timelineEvents.value[index]
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
      return data
    };

    async function updateRecipes(events: RecipeTimelineEventOut[]) {
        const recipePromises: Promise<Recipe | null>[] = [];
        const seenRecipeIds: string[] = [];
        events.forEach(event => {
          if (seenRecipeIds.includes(event.recipeId) || recipes.has(event.recipeId)) {
            return;
          }

          seenRecipeIds.push(event.recipeId);
          recipePromises.push(getRecipe(event.recipeId));
        })

        const results = await Promise.all(recipePromises);
        results.forEach(result => {
          if (result && result.id) {
            recipes.set(result.id, result);
          }
        })
    }

    async function scrollTimelineEvents() {
      const orderBy = "timestamp";
      const orderDirection = preferences.value.orderDirection === "asc" ? "asc" : "desc";

      const response = await api.recipes.getAllTimelineEvents(page.value, perPage, { orderBy, orderDirection, queryFilter: props.queryFilter });
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
      useAsync(async () => {
        if (!hasMore.value || loading.value) {
          return;
        }

        loading.value = true;
        await scrollTimelineEvents();
        loading.value = false;
      }, useAsyncKey());
    }, 500);

    // preload events
    initializeTimelineEvents();

    return {
      deleteTimelineEvent,
      loading,
      onScroll,
      preferences,
      recipes,
      reverseSort,
      timelineEvents,
      updateTimelineEvent,
    };
  },
});
</script>
