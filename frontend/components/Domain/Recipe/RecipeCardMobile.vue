<template>
  <v-expand-transition>
    <v-card
      :ripple="false"
      class="mx-auto"
      hover
      :to="$listeners.selected ? undefined : `/recipe/${slug}`"
      @click="$emit('selected')"
    >
      <v-list-item three-line>
        <slot name="avatar">
          <v-list-item-avatar tile size="125" class="v-mobile-img rounded-sm my-0 ml-n4">
            <RecipeCardImage
              :icon-size="100"
              :height="125"
              :slug="slug"
              :recipe-id="recipeId"
              small
              :image-version="image"
            ></RecipeCardImage>
          </v-list-item-avatar>
        </slot>
        <v-list-item-content>
          <v-list-item-title class="mb-1">{{ name }} </v-list-item-title>
          <v-list-item-subtitle> {{ description }} </v-list-item-subtitle>
          <div class="d-flex justify-center align-center">
            <slot name="actions">
              <RecipeFavoriteBadge v-if="loggedIn" :slug="slug" show-always />
              <v-rating
                color="secondary"
                class="ml-auto"
                background-color="secondary lighten-3"
                dense
                length="5"
                size="15"
                :value="rating"
              ></v-rating>
              <v-spacer></v-spacer>
              <RecipeContextMenu
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
                  share: true,
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
  },
  setup() {
    const { $auth } = useContext();
    const loggedIn = computed(() => {
      return $auth.loggedIn;
    });

    return {
      loggedIn,
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
</style>
