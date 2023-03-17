<template>
  <v-card
    v-if="timelineEvents && timelineEvents.length"
    height="fit-content"
    :max-height="maxHeight"
    width="100%"
    class="px-1"
    :style="maxHeight ? 'overflow-y: auto;' : ''"
  >
    <v-timeline :dense="attrs.timeline.dense" class="timeline">
      <v-timeline-item
        v-for="(event, index) in timelineEvents"
        :key="event.id"
        :class="attrs.timeline.item.class"
        fill-dot
        :small="attrs.timeline.item.small"
        :icon="chooseEventIcon(event)"
      >
        <template v-if="!useMobileFormat" #opposite>
          <v-chip v-if="event.timestamp" label large>
            <v-icon class="mr-1"> {{ $globals.icons.calendar }} </v-icon>
            {{ new Date(event.timestamp+"Z").toLocaleDateString($i18n.locale) }}
          </v-chip>
        </template>
        <v-card>
          <v-sheet>
            <v-card-title>
              <v-row>
                <v-col align-self="center" :cols="useMobileFormat ? 'auto' : '2'" :class="attrs.timeline.item.avatar.class">
                  <UserAvatar :user-id="event.userId" :size="attrs.timeline.item.avatar.size" />
                </v-col>
                <v-col v-if="useMobileFormat" align-self="center" class="pr-0">
                  <v-chip label>
                    <v-icon> {{ $globals.icons.calendar }} </v-icon>
                    {{ new Date(event.timestamp+"Z").toLocaleDateString($i18n.locale) }}
                  </v-chip>
                </v-col>
                <v-col v-else cols="9" style="margin: auto; text-align: center;">
                  {{ event.subject }}
                </v-col>
                <v-spacer />
                <v-col :cols="useMobileFormat ? 'auto' : '1'" class="px-0">
                  <RecipeTimelineContextMenu
                    v-if="$auth.user && $auth.user.id == event.userId && event.eventType != 'system'"
                    :menu-top="false"
                    :event="event"
                    :menu-icon="$globals.icons.dotsVertical"
                    fab
                    color="transparent"
                    :elevation="0"
                    :card-menu="false"
                    :use-items="{
                      edit: true,
                      delete: true,
                    }"
                    @update="updateTimelineEvent(index)"
                    @delete="deleteTimelineEvent(index)"
                  />
                </v-col>
              </v-row>
            </v-card-title>
            <v-sheet v-if="showRecipeCards && recipes.get(event.recipeId)">
              <v-row class="pt-3 pb-7 mx-3" style="max-width: 100%;">
                <v-col align-self="center" class="pa-0">
                  <RecipeCardMobile
                    :vertical="useMobileFormat"
                    :name="recipes.get(event.recipeId).name"
                    :slug="recipes.get(event.recipeId).slug"
                    :description="recipes.get(event.recipeId).description"
                    :rating="recipes.get(event.recipeId).rating"
                    :image="recipes.get(event.recipeId).image"
                    :recipe-id="recipes.get(event.recipeId).id"
                  />
                </v-col>
              </v-row>
            </v-sheet>
            <v-divider v-if="showRecipeCards && recipes.get(event.recipeId) && (useMobileFormat || event.eventMessage)" />
            <v-card-text>
              <v-row>
                <v-col>
                  <strong v-if="useMobileFormat">{{ event.subject }}</strong>
                  <div v-if="event.eventMessage" :class="useMobileFormat ? 'text-caption' : ''">
                    {{ event.eventMessage }}
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-sheet>
        </v-card>
      </v-timeline-item>
    </v-timeline>
  </v-card>
  <v-card v-else-if="!showRecipeCards">
    <v-card-title class="justify-center pa-9">
      {{ $t("recipe.timeline-is-empty") }}
    </v-card-title>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import { whenever } from "@vueuse/core";
import RecipeCardMobile from "./RecipeCardMobile.vue";
import RecipeTimelineContextMenu from "./RecipeTimelineContextMenu.vue";
import { alert } from "~/composables/use-toast";
import { useUserApi } from "~/composables/api";
import { Recipe, RecipeTimelineEventOut, RecipeTimelineEventUpdate } from "~/lib/api/types/recipe"
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";

export default defineComponent({
  components: { RecipeCardMobile, RecipeTimelineContextMenu, UserAvatar },

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

  setup(props, context) {
    const api = useUserApi();
    const { $globals, $vuetify, i18n } = useContext();
    const timelineEvents = ref([] as RecipeTimelineEventOut[]);
    const recipes = new Map<string, Recipe>();

    const useMobileFormat = computed(() => {
      return $vuetify.breakpoint.smAndDown;
    });

    const attrs = computed(() => {
      if (useMobileFormat.value) {
        return {
          timeline: {
            dense: true,
            item: {
              class: "px-0",
              small: false,
              avatar: {
                size: "30px",
                class: "pr-0",
              },
            }
          }
        }
      }
      else {
        return {
          timeline: {
            dense: false,
            item: {
              class: "px-3",
              small: false,
              avatar: {
                size: "42px",
                class: "",
              },
            }
          }
        }
      }
    })

    // V-Model Support
    const dialog = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
      },
    });

    whenever(
      () => props.value,
      () => {
        refreshTimelineEvents();
      }
    );

    function chooseEventIcon(event: RecipeTimelineEventOut) {
      switch (event.eventType) {
        case "comment":
          return $globals.icons.commentTextMultiple;

        case "info":
          return $globals.icons.informationVariant;

        case "system":
          return $globals.icons.cog;

        default:
          return $globals.icons.informationVariant;
      };
    };

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
      attrs,
      chooseEventIcon,
      deleteTimelineEvent,
      dialog,
      recipes,
      refreshTimelineEvents,
      timelineEvents,
      updateTimelineEvent,
      useMobileFormat,
    };
  },
});
</script>
