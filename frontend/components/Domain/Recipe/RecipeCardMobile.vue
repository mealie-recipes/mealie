<template>
  <v-expand-transition>
    <v-card
      :ripple="false"
      :class="isFlat ? 'mx-auto flat' : 'mx-auto'"
      hover
      :to="$listeners.selected ? undefined : recipeRoute"
      @click="$emit('selected')"
    >
      <v-img v-if="vertical" class="rounded-sm">
        <RecipeCardImage
          :icon-size="100"
          :height="150"
          :slug="slug"
          :recipe-id="recipeId"
          small
          :image-version="image"
        />
      </v-img>
      <v-list-item three-line :class="vertical ? 'px-2' : 'px-0'">
        <slot v-if="!vertical" name="avatar">
          <v-list-item-avatar tile size="125" class="v-mobile-img rounded-sm my-0">
            <RecipeCardImage
              :icon-size="100"
              :height="125"
              :slug="slug"
              :recipe-id="recipeId"
              small
              :image-version="image"
            />
          </v-list-item-avatar>
        </slot>
        <v-list-item-content class="py-0">
          <v-list-item-title class="mt-3 mb-1">{{ name }} </v-list-item-title>
          <v-list-item-subtitle>
            <SafeMarkdown :source="description" />
          </v-list-item-subtitle>
          <div class="d-flex flex-wrap justify-end align-center">
            <slot name="actions">
              <RecipeFavoriteBadge v-if="loggedIn" :slug="slug" show-always />
              <v-rating
                color="secondary"
                :class="loggedIn ? 'ml-auto' : 'ml-auto pb-2'"
                background-color="secondary lighten-3"
                dense
                length="5"
                size="15"
                :value="rating"
              ></v-rating>
              <v-spacer></v-spacer>

              <!-- If we're not logged-in, no items display, so we hide this menu -->
              <!-- We also add padding to the v-rating above to compensate -->
              <RecipeContextMenu
                v-if="loggedIn"
                :slug="slug"
                :menu-icon="$globals.icons.dotsHorizontal"
                :name="name"
                :recipe-id="recipeId"
                :use-items="{
                  delete: false,
                  edit: true,
                  download: true,
                  mealplanner: true,
                  shoppingList: true,
                  print: false,
                  printPreferences: false,
                  share: true,
                  publicUrl: false,
                }"
                @deleted="$emit('delete', slug)"
              />
            </slot>
          </div>
        </v-list-item-content>
      </v-list-item>
      <slot />
    </v-card>
  </v-expand-transition>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import RecipeFavoriteBadge from "./RecipeFavoriteBadge.vue";
import RecipeContextMenu from "./RecipeContextMenu.vue";
import RecipeCardImage from "./RecipeCardImage.vue";

export default defineComponent({
  components: {
    RecipeFavoriteBadge,
    RecipeContextMenu,
    RecipeCardImage,
  },
  props: {
    name: {
      type: String,
      required: true,
    },
    groupSlug: {
      type: String,
      default: null,
    },
    slug: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    rating: {
      type: Number,
      default: 0,
    },
    image: {
      type: String,
      required: false,
      default: "abc123",
    },
    route: {
      type: Boolean,
      default: true,
    },
    recipeId: {
      type: String,
      required: true,
    },
    vertical: {
      type: Boolean,
      default: false,
    },
    isFlat: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const { $auth } = useContext();
    const loggedIn = computed(() => {
      return $auth.loggedIn;
    });

    const recipeRoute = computed<string>(() => {
      return loggedIn.value ? `/recipe/${props.slug}` : `/explore/recipes/${props.groupSlug}/${props.slug}`;
    });

    return {
      loggedIn,
      recipeRoute,
    };
  },
});
</script>

<style>
.v-mobile-img {
  padding-top: 0;
  padding-bottom: 0;
  padding-left: 0;
}
.v-card--reveal {
  align-items: center;
  bottom: 0;
  justify-content: center;
  opacity: 0.8;
  position: absolute;
  width: 100%;
}
.v-card--text-show {
  opacity: 1 !important;
}
.headerClass {
  white-space: nowrap;
  word-break: normal;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-top {
  align-self: start !important;
}

.flat, .theme--dark .flat {
  box-shadow: none!important;
  background-color: transparent!important;
}
</style>
