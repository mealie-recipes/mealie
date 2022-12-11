<template>
  <BaseDialog
    v-model="dialog"
    :title="attrs.title"
    :icon="$globals.icons.timelineText"
    width="70%"
  >
    <v-card
      v-if="timelineEvents && timelineEvents.length"
      height="fit-content"
      max-height="70vh"
      width="100%"
      style="overflow-y: auto;"
    >
      <v-timeline :dense="attrs.timeline.dense">
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
                  <v-col align-self="center" :cols="useMobileFormat ? 'auto' : '2'">
                    <UserAvatar :user-id="event.userId" />
                  </v-col>
                  <v-col v-if="useMobileFormat" align-self="center" class="ml-3">
                    <v-chip label>
                      <v-icon> {{ $globals.icons.calendar }} </v-icon>
                      {{ new Date(event.timestamp+"Z").toLocaleDateString($i18n.locale) }}
                    </v-chip>
                  </v-col>
                  <v-col v-else cols="9">
                    {{ event.subject }}
                  </v-col>
                  <v-spacer />
                  <v-col :cols="useMobileFormat ? 'auto' : '1'" :class="useMobileFormat ? '' : 'pa-0'">
                    <RecipeTimelineContextMenu
                      v-if="$auth.user && $auth.user.id == event.userId && event.eventType != 'system'"
                      :menu-top="false"
                      :slug="slug"
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
    <v-card v-else>
      <v-card-title class="justify-center pa-9">
        {{ $t("recipe.timeline-is-empty") }}
      </v-card-title>
    </v-card>
  </BaseDialog>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import { whenever } from "@vueuse/core";
import RecipeTimelineContextMenu from "./RecipeTimelineContextMenu.vue";
import { alert } from "~/composables/use-toast";
import { useUserApi } from "~/composables/api";
import { RecipeTimelineEventOut, RecipeTimelineEventUpdate } from "~/lib/api/types/recipe"
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
    const { $globals, $vuetify, i18n } = useContext();
    const timelineEvents = ref([{}] as RecipeTimelineEventOut[])

    const useMobileFormat = computed(() => {
      return $vuetify.breakpoint.smAndDown;
    });

    const attrs = computed(() => {
      if (useMobileFormat.value) {
        return {
          title: i18n.tc("recipe.timeline"),
          timeline: {
            dense: true,
            item: {
              class: "pr-3",
              small: true
            }
          }
        }
      }
      else {
        return {
          title: `${i18n.tc("recipe.timeline")} – ${props.recipeName}`,
          timeline: {
            dense: false,
            item: {
              class: "px-3",
              small: false
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

    async function updateTimelineEvent(index: number) {
      const event = timelineEvents.value[index]
      const payload: RecipeTimelineEventUpdate = {
        subject: event.subject,
        eventMessage: event.eventMessage,
        image: event.image,
      };

        const { response } = await api.recipes.updateTimelineEvent(props.slug, event.id, payload);
        if (response?.status !== 200) {
          alert.error(i18n.t("events.something-went-wrong") as string);
          return;
        }

        alert.success(i18n.t("events.event-updated") as string);
      };

    async function deleteTimelineEvent(index: number) {
      const { response } = await api.recipes.deleteTimelineEvent(props.slug, timelineEvents.value[index].id);
      if (response?.status !== 200) {
        alert.error(i18n.t("events.something-went-wrong") as string);
        return;
      }

      timelineEvents.value.splice(index, 1);
      alert.success(i18n.t("events.event-deleted") as string);
    };

    async function refreshTimelineEvents() {
      // TODO: implement infinite scroll and paginate instead of loading all events at once
      const page = 1;
      const perPage = -1;
      const orderBy = "timestamp";
      const orderDirection = "asc";

      const response = await api.recipes.getAllTimelineEvents(props.slug, page, perPage, { orderBy, orderDirection });
      if (!response?.data) {
        return;
      }

      timelineEvents.value = response.data.items;
    };

    // preload events
    refreshTimelineEvents();

    return {
      attrs,
      chooseEventIcon,
      deleteTimelineEvent,
      dialog,
      refreshTimelineEvents,
      timelineEvents,
      updateTimelineEvent,
      useMobileFormat,
    };
  },
});
</script>
