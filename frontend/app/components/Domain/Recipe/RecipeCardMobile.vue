<template>
  <div :style="`height: ${height}px;`">
    <v-expand-transition>
      <v-card
        :ripple="false"
        :class="[
          isFlat ? 'mx-auto flat' : 'mx-auto mealie-row-card',
          { 'disable-highlight': disableHighlight },
        ]"
        :style="{ cursor }"
        :elevation="0"
        height="100%"
        :to="$attrs.selected ? undefined : recipeRoute"
        @click="$emit('selected')"
      >
        <v-img
          v-if="vertical"
          class="rounded-sm"
          cover
        >
          <RecipeCardImage
            tiny
            :icon-size="100"
            :slug="slug"
            :recipe-id="recipeId"
            :image-version="image"
            :height="height"
          />
        </v-img>
        <v-list-item
          lines="two"
          class="py-0"
          :class="vertical ? 'px-2' : 'px-0'"
          item-props
          height="100%"
          density="compact"
        >
          <template #prepend>
            <slot
              v-if="!vertical"
              name="avatar"
            >
              <RecipeCardImage
                tiny
                :icon-size="100"
                :slug="slug"
                :recipe-id="recipeId"
                :image-version="image"
                width="125"
                :height="height"
              />
            </slot>
          </template>
          <div class="pl-4 d-flex flex-column justify-space-between align-stretch pr-2">
            <v-list-item-title class="mt-3 mb-1 text-top text-truncate w-100 mealie-row-card__title">
              {{ name }}
            </v-list-item-title>
            <v-list-item-subtitle class="ma-0 text-top mealie-row-card__description">
              <SafeMarkdown v-if="description" :source="description" />
              <p v-else>
                <br>
                <br>
                <br>
              </p>
            </v-list-item-subtitle>
            <div
              class="d-flex flex-nowrap justify-start ma-0 pt-2 pb-0"
              style="overflow-x: hidden; overflow-y: hidden; white-space: nowrap;"
            >
              <RecipeChips
                :truncate="true"
                :items="tags"
                :title="false"
                :limit="2"
                small
                url-prefix="tags"
                v-bind="$attrs"
              />
            </div>
          </div>
          <slot name="actions">
            <v-card-actions class="w-100 my-0 px-1 py-0">
              <RecipeFavoriteBadge
                v-if="isOwnGroup && showRecipeContent"
                :recipe-id="recipeId"
                show-always
                class="ma-0 pa-0"
              />
              <div v-else class="my-0 px-1 py-0" /> <!-- Empty div to keep the layout consistent -->
              <RecipeCardRating
                v-if="showRecipeContent"
                :class="[{ 'pb-2': !isOwnGroup }, 'ml-n2']"
                :model-value="rating"
                :recipe-id="recipeId"
              />

              <!-- If we're not logged-in, no items display, so we hide this menu -->
              <!-- We also add padding to the v-rating above to compensate -->
              <slot name="context-menu">
                <RecipeContextMenu
                  v-if="isOwnGroup && showRecipeContent"
                  :slug="slug"
                  :menu-icon="$globals.icons.dotsHorizontal"
                  :name="name"
                  :recipe-id="recipeId"
                  class="ml-auto"
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
                  :leading-items="contextMenuLeadingItems"
                  :append-items="contextMenuAppendItems"
                  @deleted="$emit('delete', slug)"
                  @mealplan-remove="$emit('mealplanRemove')"
                  @mealplan-edit="$emit('mealplanEdit')"
                />
              </slot>
            </v-card-actions>
          </slot>
        </v-list-item>
        <slot />
      </v-card>
    </v-expand-transition>
  </div>
</template>

<script setup lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import RecipeCardImage from "./RecipeCardImage.vue";
import RecipeCardRating from "./RecipeCardRating.vue";
import RecipeChips from "./RecipeChips.vue";
import RecipeContextMenu from "./RecipeContextMenu/RecipeContextMenu.vue";
import RecipeFavoriteBadge from "./RecipeFavoriteBadge.vue";
import type { ContextMenuItem } from "./RecipeContextMenu/RecipeContextMenu.vue";

interface Props {
  name: string;
  slug: string;
  description: string;
  rating?: number;
  image?: string;
  tags?: Array<any>;
  recipeId: string;
  vertical?: boolean;
  isFlat?: boolean;
  height?: number;
  disableHighlight?: boolean;
  contextMenuAppendItems?: ContextMenuItem[];
  contextMenuLeadingItems?: ContextMenuItem[];
}
const props = withDefaults(defineProps<Props>(), {
  rating: 0,
  image: undefined,
  tags: () => [],
  vertical: false,
  isFlat: false,
  height: 150,
  disableHighlight: false,
});

defineEmits<{
  mealplanRemove: [];
  mealplanEdit: [];
  selected: [];
  delete: [slug: string];
}>();

const auth = useMealieAuth();
const { isOwnGroup } = useLoggedInState();

const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug || auth.user.value?.groupSlug || "");
const showRecipeContent = computed(() => props.recipeId && props.slug);
const recipeRoute = computed<string>(() => {
  return showRecipeContent.value ? `/g/${groupSlug.value}/r/${props.slug}` : "";
});
const cursor = computed(() => showRecipeContent.value ? "pointer" : "auto");
</script>

<style scoped>
:deep(.v-list-item__prepend) {
  height: 100%;
}
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

.flat,
.theme--dark .flat {
  box-shadow: none !important;
  background-color: transparent !important;
}

.mealie-row-card {
  border-radius: 16px !important;
  background: var(--mealie-surface) !important;
  box-shadow: inset 0 0 0 1px var(--mealie-hairline-strong) !important;
  transition: box-shadow 0.2s ease;
}

.mealie-row-card:hover {
  box-shadow:
    0 12px 28px -16px rgba(40, 30, 20, 0.35),
    inset 0 0 0 1px var(--mealie-hairline-strong) !important;
}

.mealie-row-card :deep(.v-list-item__prepend) {
  padding: 6px 0 6px 6px;
}

.mealie-row-card :deep(.v-list-item__prepend .v-img),
.mealie-row-card :deep(.v-list-item__prepend .v-responsive) {
  border-radius: 12px;
  overflow: hidden;
}

.mealie-row-card__title {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.mealie-row-card__description {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
  font-size: 13px;
  color: var(--mealie-text-tertiary);
  opacity: 1;
}

.disable-highlight :deep(.v-card__overlay) {
  opacity: 0 !important;
}
</style>
