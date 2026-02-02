<template>
  <v-timeline-item :class="attrs.class" fill-dot :small="attrs.small" :icon="icon" dot-color="primary">
    <template v-if="!useMobileFormat" #opposite>
      <v-chip v-if="event.timestamp" label large>
        <v-icon class="mr-1">
          {{ $globals.icons.calendar }}
        </v-icon>
        {{ $d(new Date(event.timestamp)) }}
      </v-chip>
    </template>
    <v-card
      hover
      :to="$attrs.selected || !recipe ? undefined : `/g/${groupSlug}/r/${recipe.slug}`"
      class="elevation-12"
      @click="$emit('selected')"
    >
      <v-card-title class="background">
        <v-row>
          <v-col align-self="center" :cols="useMobileFormat ? 'auto' : '2'" :class="attrs.avatar.class">
            <UserAvatar :user-id="event.userId" :size="attrs.avatar.size" />
          </v-col>
          <v-col v-if="useMobileFormat" align-self="center" class="pr-0">
            <v-chip label>
              <v-icon> {{ $globals.icons.calendar }} </v-icon>
              {{ $d(new Date(event.timestamp || "")) }}
            </v-chip>
          </v-col>
          <v-col v-else cols="9" style="margin: auto; text-align: center">
            {{ event.subject }}
          </v-col>
          <v-spacer />
          <v-col :cols="useMobileFormat ? 'auto' : '1'" class="px-0 pt-0">
            <RecipeTimelineContextMenu
              v-if="currentUser && currentUser.id == event.userId && event.eventType != 'system'"
              :menu-top="false"
              :event="event"
              :menu-icon="$globals.icons.dotsVertical"
              color="transparent"
              :elevation="0"
              :card-menu="false"
              :use-items="{
                edit: true,
                delete: true,
              }"
              @update="$emit('update', $event)"
              @delete="$emit('delete')"
            />
          </v-col>
        </v-row>
      </v-card-title>
      <v-card-text v-if="showRecipeCards && recipe" class="background">
        <v-row :class="useMobileFormat ? 'py-3 mx-0' : 'py-3 mx-0'" style="max-width: 100%">
          <v-col align-self="center" class="pa-0">
            <RecipeCardMobile
              disable-highlight
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
      <v-divider v-if="showRecipeCards && recipe && (useMobileFormat || event.eventMessage)" />
      <v-card-text class="background">
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
              :class="attrs.image.class"
              @error="hideImage = true"
            />
            <div v-if="event.eventMessage" :class="useMobileFormat ? 'text-caption' : ''">
              <SafeMarkdown :source="event.eventMessage" />
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-timeline-item>
</template>

<script setup lang="ts">
import RecipeCardMobile from "./RecipeCardMobile.vue";
import RecipeTimelineContextMenu from "./RecipeTimelineContextMenu.vue";
import { useStaticRoutes } from "~/composables/api";
import { useTimelineEventTypes } from "~/composables/recipes/use-recipe-timeline-events";
import type { Recipe, RecipeTimelineEventOut, RecipeTimelineEventUpdate } from "~/lib/api/types/recipe";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import SafeMarkdown from "~/components/global/SafeMarkdown.vue";

interface Props {
  event: RecipeTimelineEventOut;
  recipe?: Recipe;
  showRecipeCards?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  recipe: undefined,
  showRecipeCards: false,
});

defineEmits<{
  selected: [];
  update: [event: RecipeTimelineEventUpdate];
  delete: [];
}>();

const { $globals } = useNuxtApp();
const display = useDisplay();
const { recipeTimelineEventSmallImage } = useStaticRoutes();
const { eventTypeOptions } = useTimelineEventTypes();

const { user: currentUser } = useMealieAuth();

const route = useRoute();
const groupSlug = computed(() => (route.params.groupSlug as string) || currentUser?.value?.groupSlug || "");

const useMobileFormat = computed(() => {
  return display.smAndDown.value;
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
        class: "my-3",
      },
    };
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
        class: "mb-5",
      },
    };
  }
});

const icon = computed(() => {
  const option = eventTypeOptions.value.find(option => option.value === props.event.eventType);
  return option ? option.icon : $globals.icons.informationVariant;
});

const hideImage = ref(false);
const eventImageUrl = computed<string>(() => {
  if (props.event.image !== "has image") {
    return "";
  }

  return recipeTimelineEventSmallImage(props.event.recipeId, props.event.id);
});
</script>

<style>
.v-card::after {
  display: none;
}
</style>
