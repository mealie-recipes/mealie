<template>
    <BaseDialog
        v-model="dialog"
        :title="`Timeline – ${recipeName}`"
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
                    <div class="mr-3"><UserAvatar :user-id="event.userId" /></div>
                    {{ event.subject }}
                  </v-card-title>
                  <v-card-text v-if="event.message">
                    {{ event.message }}
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
      </BaseDialog>
  </template>

  <script lang="ts">
  import { computed, defineComponent, ref, useContext, } from "@nuxtjs/composition-api";
  import { whenever } from "@vueuse/core";
  import { RecipeTimelineEventOut } from "~/lib/api/types/recipe"
  import { RequestResponse } from "~/lib/api/types/non-generated";
  import UserAvatar from "~/components/Domain/User/UserAvatar.vue";

  export default defineComponent({
    components: { UserAvatar },

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

      const timelineEvents = ref([{}] as RecipeTimelineEventOut[])
      const { $axios, $globals } = useContext();

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
        // TODO: implement this properly when PR #1801 is merged
        // TODO: switch message to eventMessage when PR #1801 is merged
        // TODO: implement infinite scroll and paginate

        console.error("Using temporary API implementation; not suitable for production!!!");

        function getRequests() {
          return {
            async get<T>(url: string, params = {}): Promise<RequestResponse<any>> {
              let error = null;
              const response = await $axios.get<T>(url, params).catch((e) => {
                error = e;
              });
              if (response != null) {
                return { response, error, data: response?.data };
              }
              return { response: null, error, data: null };
            }
          };
        }

        const url = `/api/recipes/${props.slug}/timeline/events?orderBy=timestamp&orderDirection=asc&perPage=-1`
        const response = await getRequests().get(url)
        timelineEvents.value = response.data.items;
      };

      // preload events
      refreshTimelineEvents();

      return {
        chooseEventIcon,
        dialog,
        timelineEvents,
      };
    },
  });
  </script>
