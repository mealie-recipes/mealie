<template>
  <BaseDialog
    v-model="dialog"
    :title="useMobileFormat ? 'Timeline' : `Timeline – ${recipeName}`"
    :icon="$globals.icons.timelineText"
    width="70%"
  >
    <!-- Desktop -->
    <div v-if="!useMobileFormat">
      <v-card
        v-if="timelineEvents && timelineEvents.length"
        height="fit-content"
        max-height="70vh"
        width="100%"
        style="overflow-y: auto;"
      >
        <v-timeline>
          <v-timeline-item
            v-for="event in timelineEvents"
            :key="event.id"
            class="px-3"
            fill-dot
            :icon="chooseEventIcon(event)"
          >
            <template #opposite>
              <v-chip v-if="event.timestamp" label large>
                <v-icon class="mr-1"> {{ $globals.icons.calendar }} </v-icon>
                {{ new Date(event.timestamp).toLocaleDateString($i18n.locale) }}
              </v-chip>
            </template>
            <v-card>
              <v-sheet>
                <v-card-title>
                  <v-row>
                    <v-col cols="auto">
                      <div class="mr-1" style="display: inline;"><UserAvatar :user-id="event.userId" /></div>
                      {{ event.subject }}
                    </v-col>
                    <v-spacer />
                    <v-col cols="auto" class="pa-0">
                      <RecipeTimelineContextMenu
                        v-if="$auth.user && $auth.user.id == event.userId && event.eventType != 'system'"
                        :menu-top="false"
                        :slug="slug"
                        :event-id="event.id"
                        :menu-icon="$globals.icons.dotsVertical"
                        fab
                        color="transparent"
                        :elevation="0"
                        :card-menu="false"
                        :use-items="{
                          edit: true,
                          delete: true,
                        }"
                      />
                    </v-col>
                  </v-row>
                </v-card-title>
                <v-card-text v-if="event.eventMessage">
                  {{ event.eventMessage }}
                </v-card-text>
              </v-sheet>
            </v-card>
          </v-timeline-item>
        </v-timeline>
      </v-card>
      <v-card v-else>
        <v-card-title class="justify-center">
          Nothing on the timeline yet. Try making this recipe!
        </v-card-title>
      </v-card>
    </div>

    <!-- Mobile | Dense -->
    <div v-else>
      <v-card
        v-if="timelineEvents && timelineEvents.length"
        height="fit-content"
        max-height="70vh"
        width="100%"
        style="overflow-y: auto;"
      >
        <v-timeline dense>
          <v-timeline-item
            v-for="event in timelineEvents"
            :key="event.id"
            class="pr-3 mb-9"
            fill-dot
            small
            :icon="chooseEventIcon(event)"
          >
            <v-row v-if="event.timestamp" no-gutters class="mb-1">
              <v-col align-self="center" cols="auto">
                <UserAvatar :user-id="event.userId" />
              </v-col>
              <v-col align-self="center" class="ml-3">
                <v-chip label small>
                  <v-icon> {{ $globals.icons.calendar }} </v-icon>
                  {{ new Date(event.timestamp).toLocaleDateString($i18n.locale) }}
                </v-chip>
              </v-col>
              <v-spacer />
                <v-col cols="auto">
                  <RecipeTimelineContextMenu
                    v-if="$auth.user && $auth.user.id == event.userId && event.eventType != 'system'"
                    :menu-top="false"
                    :slug="slug"
                    :event-id="event.id"
                    :menu-icon="$globals.icons.dotsVertical"
                    fab
                    color="transparent"
                    :elevation="0"
                    :card-menu="false"
                    :use-items="{
                      edit: true,
                      delete: true,
                    }"
                  />
                </v-col>
            </v-row>
            <v-row no-gutters class="mt-0">
              <v-col>
                <strong>{{ event.subject }}</strong>
                <div v-if="event.eventMessage" class="text-caption">
                  {{ event.eventMessage }}
                </div>
              </v-col>
            </v-row>
          </v-timeline-item>
        </v-timeline>
      </v-card>
      <v-card v-else>
        <v-card-text class="justify-center pa-1">
          Nothing on the timeline yet. Try making this recipe!
        </v-card-text>
      </v-card>
    </div>

  </BaseDialog>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext, } from "@nuxtjs/composition-api";
import { whenever } from "@vueuse/core";
import RecipeTimelineContextMenu from "./RecipeTimelineContextMenu.vue";
import { useUserApi } from "~/composables/api";
import { RecipeTimelineEventOut } from "~/lib/api/types/recipe"
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";

export default defineComponent({
  components: { RecipeTimelineContextMenu, UserAvatar },

  props: {
    value: {
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

  setup(props, context) {
    const api = useUserApi();
    const { $globals, $vuetify } = useContext();
    const timelineEvents = ref([{}] as RecipeTimelineEventOut[])

    const useMobileFormat = computed(() => {
      return $vuetify.breakpoint.smAndDown;
    });

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

    async function refreshTimelineEvents() {
      // TODO: implement infinite scroll and paginate instead of loading all events at once
      const page = 1;
      const perPage = -1;
      const orderBy = "timestamp";
      const orderDirection = "asc";

      const response = await api.recipes.getAllTimelineEvents(props.slug, page, perPage, { orderBy, orderDirection })
      if (!response?.data) {
        return;
      }

      timelineEvents.value = response.data.items;
    };

    // preload events
    refreshTimelineEvents();

    return {
      chooseEventIcon,
      dialog,
      timelineEvents,
      useMobileFormat,
    };
  },
});
</script>
