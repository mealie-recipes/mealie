<template>
  <v-card
    v-if="timelineEvents && timelineEvents.length"
    height="fit-content"
    :max-height="maxHeight"
    width="100%"
    class="px-1"
    :style="maxHeight ? 'overflow-y: auto;' : ''"
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
  <v-card v-else-if="!showRecipeCards">
    <v-card-title class="justify-center pa-9">
      {{ $t("recipe.timeline-is-empty") }}
    </v-card-title>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import { whenever } from "@vueuse/core";
import RecipeTimelineItem from "./RecipeTimelineItem.vue"
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
    const timelineEvents = ref([] as RecipeTimelineEventOut[]);
    const recipes = new Map<string, Recipe>();

    whenever(
      () => props.value,
      () => {
        refreshTimelineEvents();
      }
    );

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

    async function refreshTimelineEvents() {
      // TODO: implement infinite scroll and paginate instead of loading all events and recipes at once
      const page = 1;
      const perPage = -1;
      const orderBy = "timestamp";
      const orderDirection = "asc";

      const response = await api.recipes.getAllTimelineEvents(page, perPage, { orderBy, orderDirection, queryFilter: props.queryFilter });
      if (!response?.data) {
        return;
      }

      const events = response.data.items;

      // fetch recipes
      if (props.showRecipeCards) {
        await updateRecipes(events);
      }

      // this is set last so Vue know to re-render
      timelineEvents.value = events;
    };

    // preload events
    refreshTimelineEvents();

    return {
      deleteTimelineEvent,
      recipes,
      refreshTimelineEvents,
      timelineEvents,
      updateTimelineEvent,
    };
  },
});
</script>
