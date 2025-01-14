<template>
  <div :style="`height: ${height}`">
    <v-expand-transition>
      <v-card
        :ripple="false"
        :class="isFlat ? 'mx-auto flat' : 'mx-auto'"
        :style="{ cursor }"
        hover
        :to="$listeners.selected ? undefined : recipeRoute"
        @click="$emit('selected')"
      >
        <v-img v-if="vertical" class="rounded-sm">
          <RecipeCardImage
            :icon-size="100"
            :height="height"
            :slug="slug"
            :recipe-id="recipeId"
            small
            :image-version="image"
          />
        </v-img>
        <v-list-item three-line :class="vertical ? 'px-2' : 'px-0'">
          <slot v-if="!vertical" name="avatar">
            <v-list-item-avatar tile :height="height" width="125" class="v-mobile-img rounded-sm my-0">
              <RecipeCardImage
                :icon-size="100"
                :height="height"
                :slug="slug"
                :recipe-id="recipeId"
                :image-version="image"
                small
              />
            </v-list-item-avatar>
          </slot>
          <v-list-item-content class="py-0">
            <v-list-item-title class="mt-1 mb-1 text-top">{{ name }}</v-list-item-title>
            <v-list-item-subtitle class="ma-0 text-top">
              <SafeMarkdown :source="description" />
            </v-list-item-subtitle>
            <div class="d-flex flex-wrap justify-start ma-0">
              <RecipeChips :truncate="true" :items="tags" :title="false" :limit="2" :small="true" url-prefix="tags" v-on="$listeners" />
            </div>
            <div class="d-flex flex-wrap justify-end align-center">
              <slot name="actions">
                <RecipeFavoriteBadge v-if="isOwnGroup && showRecipeContent" :recipe-id="recipeId" show-always />
                <RecipeRating
                  v-if="showRecipeContent"
                  :class="isOwnGroup ? 'ml-auto' : 'ml-auto pb-2'"
                  :value="rating"
                  :recipe-id="recipeId"
                  :slug="slug"
                  :small="true"
                />
                <v-spacer></v-spacer>

                <!-- If we're not logged-in, no items display, so we hide this menu -->
                <!-- We also add padding to the v-rating above to compensate -->
                <RecipeContextMenu
                  v-if="isOwnGroup && showRecipeContent"
                  :slug="slug"
                  :menu-icon="$globals.icons.dotsHorizontal"
                  :name="name"
                  :recipe-id="recipeId"
                  :use-items="{
                    delete: false,
                    edit: false,
                    download: true,
                    mealplanner: true,
                    shoppingList: true,
                    print: false,
                    printPreferences: false,
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
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext, useRoute } from "@nuxtjs/composition-api";
import RecipeFavoriteBadge from "./RecipeFavoriteBadge.vue";
import RecipeContextMenu from "./RecipeContextMenu.vue";
import RecipeCardImage from "./RecipeCardImage.vue";
import RecipeRating from "./RecipeRating.vue";
import RecipeChips from "./RecipeChips.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";

export default defineComponent({
  components: {
    RecipeFavoriteBadge,
    RecipeContextMenu,
    RecipeRating,
    RecipeCardImage,
    RecipeChips,
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
    tags: {
      type: Array,
      default: () => [],
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
    height: {
      type: [Number, String],
      default: 150,
    },
    imageHeight: {
      type: [Number, String],
      default: "fill-height",
    },
  },
  setup(props) {
    const { $auth } = useContext();
    const { isOwnGroup } = useLoggedInState();

    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");
    const showRecipeContent = computed(() => props.recipeId && props.slug);
    const recipeRoute = computed<string>(() => {
      return showRecipeContent.value ? `/g/${groupSlug.value}/r/${props.slug}` : "";
    });
    const cursor = computed(() => showRecipeContent.value ? "pointer" : "auto");


    return {
      isOwnGroup,
      recipeRoute,
      showRecipeContent,
      cursor,
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
