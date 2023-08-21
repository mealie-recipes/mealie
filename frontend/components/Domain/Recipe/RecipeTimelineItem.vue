<template>
  <v-timeline-item
    :class="attrs.class"
    fill-dot
    :small="attrs.small"
    :icon="icon"
  >
    <template v-if="!useMobileFormat" #opposite>
      <v-chip v-if="event.timestamp" label large>
        <v-icon class="mr-1"> {{ $globals.icons.calendar }} </v-icon>
        {{ new Date(event.timestamp+"Z").toLocaleDateString($i18n.locale) }}
      </v-chip>
    </template>
      <v-card
        hover
        :to="$listeners.selected ? undefined : `/recipe/${recipe.slug}`"
        @click="$emit('selected')">
        <v-sheet>
        <v-card-title class="bg-primary">
            <v-row>
            <v-col align-self="center" :cols="useMobileFormat ? 'auto' : '2'" :class="attrs.avatar.class">
                <UserAvatar :user-id="event.userId" :size="attrs.avatar.size" />
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
            <v-col :cols="useMobileFormat ? 'auto' : '1'" class="px-0 pt-0">
                <RecipeTimelineContextMenu
                v-if="$auth.user && $auth.user.id == event.userId && event.eventType != 'system'"
                :menu-top="false"
                :event="event"
                :menu-icon="$globals.icons.dotsVertical"
                :use-mobile-format="useMobileFormat"
                fab
                color="transparent"
                :elevation="0"
                :card-menu="false"
                :use-items="{
                    edit: true,
                    delete: true,
                }"
                @update="$emit('update')"
                @delete="$emit('delete')"
                />
            </v-col>
            </v-row>
        </v-card-title>
        <v-card-text v-if="showRecipeCards && recipe">
            <v-row :class="useMobileFormat ? 'py-3 mx-0' : 'py-3 mx-0'" style="max-width: 100%;">
              <v-col align-self="center" class="pa-0">
              <RecipeCardMobile
                :vertical="useMobileFormat"
                :name="recipe.name"
                :slug="recipe.slug"
                :description="recipe.description"
                :rating="recipe.rating"
                :image="recipe.image"
                :recipe-id="recipe.id"
                :is-flat="true"
              />
            </v-col>
            </v-row>
        </v-card-text>
        </v-sheet>
        <v-divider v-if="showRecipeCards && recipe && (useMobileFormat || event.eventMessage)" />
        <v-card-text v-if="showRecipeCards && recipe && (useMobileFormat || event.eventMessage)">
            <v-row>
            <v-col>
                <strong v-if="useMobileFormat">{{ event.subject }}</strong>
                <v-img
                  v-if="eventImageUrl"
                  :src="eventImageUrl"
                  min-height="50"
                  :height="hideImage ? undefined : 'auto'"
                  :max-height="attrs.image.maxHeight"
                  contain
                  :class=attrs.image.class
                  @error="hideImage = true"
                />
                <div v-if="event.eventMessage" :class="useMobileFormat ? 'text-caption' : ''">
                {{ event.eventMessage }}
                </div>
            </v-col>
            </v-row>
        </v-card-text>
    </v-card>
  </v-timeline-item>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import RecipeCardMobile from "./RecipeCardMobile.vue";
import RecipeTimelineContextMenu from "./RecipeTimelineContextMenu.vue";
import { useStaticRoutes } from "~/composables/api";
import { Recipe, RecipeTimelineEventOut } from "~/lib/api/types/recipe"
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";

export default defineComponent({
  components: { RecipeCardMobile, RecipeTimelineContextMenu, UserAvatar },

  props: {
    event: {
      type: Object as () => RecipeTimelineEventOut,
      required: true,
    },
    recipe: {
      type: Object as () => Recipe,
      default: undefined,
    },
    showRecipeCards: {
      type: Boolean,
      default: false,
    }
  },

  setup(props) {
    const { $globals, $vuetify } = useContext();
    const { recipeTimelineEventImage } = useStaticRoutes();
    const timelineEvents = ref([] as RecipeTimelineEventOut[]);

    const useMobileFormat = computed(() => {
      return $vuetify.breakpoint.smAndDown;
    });

    const attrs = computed(() => {
      if (useMobileFormat.value) {
        return {
          class: "px-0",
          small: false,
          avatar: {
            size: "30px",
            class: "pr-0",
          },
          image: {
            maxHeight: "250",
            class: "my-3"
          },
        }
      }
      else {
        return {
          class: "px-3",
          small: false,
          avatar: {
            size: "42px",
            class: "",
          },
          image: {
            maxHeight: "300",
            class: "mb-5"
          },
        }
      }
    })

    const icon = computed( () => {
      switch (props.event.eventType) {
        case "comment":
          return $globals.icons.commentTextMultiple;

        case "info":
          return $globals.icons.informationVariant;

        case "system":
          return $globals.icons.cog;

        default:
          return $globals.icons.informationVariant;
      };
    })

    const hideImage = ref(false);
    const eventImageUrl = computed<string>( () => {
      if (props.event.image !== "has image") {
        return "";
      }

      return recipeTimelineEventImage(props.event.recipeId, props.event.id);
    })

    return {
      attrs,
      icon,
      eventImageUrl,
      hideImage,
      timelineEvents,
      useMobileFormat,
    };
  },
});
</script>

<style>
.v-card::after {
  display: none;
}
</style>