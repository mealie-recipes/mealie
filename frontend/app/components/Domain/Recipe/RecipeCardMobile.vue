<template>
  <div :style="`height: ${height}px;`">
    <v-expand-transition>
      <v-card
        :ripple="false"
        :class="[
          'recipe-card',
          isFlat ? 'mx-auto flat' : 'mx-auto',
          { 'disable-highlight': disableHighlight, 'recipe-card--selected': selected },
        ]"
        :style="{ cursor }"
        hover
        height="100%"
        @click="handleCardClick"
      >
        <NuxtLink
          v-if="!selectMode && recipeRoute"
          :to="recipeRoute"
          class="recipe-card-link"
          :aria-label="name"
        />
        <v-btn
          v-if="selectMode"
          class="recipe-card-selection"
          icon
          size="small"
          variant="flat"
          color="info"
          :aria-label="selectionLabel"
          :aria-pressed="selected"
          @click.stop="$emit('selected')"
        >
          <v-icon>
            {{ selected ? $globals.icons.checkboxMarkedCircle : $globals.icons.checkboxBlankCircleOutline }}
          </v-icon>
        </v-btn>
        <div
          class="recipe-card-content"
          :class="{ 'recipe-card-content--linked': !selectMode && recipeRoute }"
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
              <v-list-item-title class="mt-3 mb-1 text-top text-truncate w-100">
                {{ name }}
              </v-list-item-title>
              <v-list-item-subtitle class="ma-0 text-top">
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
                  class="recipe-card-tags"
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
              <v-card-actions class="recipe-card-actions w-100 my-0 px-1 py-0">
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

                <v-tooltip
                  v-if="showOrganizer && !selectMode && isOwnGroup && showRecipeContent"
                  location="bottom"
                  color="info"
                >
                  <template #activator="{ props: tooltipProps }">
                    <v-btn
                      icon
                      variant="text"
                      size="small"
                      v-bind="tooltipProps"
                      :aria-label="$t('settings.organize')"
                      @click.stop.prevent="$emit('organize')"
                    >
                      <v-icon>{{ $globals.icons.organizers }}</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("settings.organize") }}</span>
                </v-tooltip>

                <!-- If we're not logged-in, no items display, so we hide this menu -->
                <!-- We also add padding to the v-rating above to compensate -->
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
                  @deleted="$emit('delete', slug)"
                />
              </v-card-actions>
            </slot>
          </v-list-item>
          <slot />
        </div>
      </v-card>
    </v-expand-transition>
  </div>
</template>

<script setup lang="ts">
import RecipeFavoriteBadge from "./RecipeFavoriteBadge.vue";
import RecipeContextMenu from "./RecipeContextMenu/RecipeContextMenu.vue";
import RecipeCardImage from "./RecipeCardImage.vue";
import RecipeCardRating from "./RecipeCardRating.vue";
import RecipeChips from "./RecipeChips.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";

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
  showOrganizer?: boolean;
  selectMode?: boolean;
  selected?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  rating: 0,
  image: "abc123",
  tags: () => [],
  vertical: false,
  isFlat: false,
  height: 150,
  disableHighlight: false,
  showOrganizer: false,
  selectMode: false,
  selected: false,
});

const emit = defineEmits<{
  selected: [];
  organize: [];
  delete: [slug: string];
}>();

const auth = useMealieAuth();
const { isOwnGroup } = useLoggedInState();
const i18n = useI18n();

const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug || auth.user.value?.groupSlug || "");
const showRecipeContent = computed(() => props.recipeId && props.slug);
const recipeRoute = computed<string>(() => {
  return showRecipeContent.value ? `/g/${groupSlug.value}/r/${props.slug}` : "";
});
const cursor = computed(() => props.selectMode || showRecipeContent.value ? "pointer" : "auto");
const selectionLabel = computed(() => i18n.t(
  props.selected ? "recipe.deselect-recipe" : "recipe.select-recipe",
  { name: props.name },
));

function handleCardClick(event: MouseEvent) {
  if (!props.selectMode) {
    return;
  }

  if (event.target instanceof Element && event.target.closest("button, a, input, select, textarea, [role='button']")) {
    return;
  }

  event.preventDefault();
  emit("selected");
}
</script>

<style scoped>
.recipe-card {
  position: relative;
}
.recipe-card-link {
  border-radius: inherit;
  inset: 0;
  position: absolute;
  z-index: 0;
}
.recipe-card-link:focus-visible {
  outline: 3px solid rgb(var(--v-theme-info));
  outline-offset: 2px;
}
.recipe-card-content {
  position: relative;
  z-index: 1;
}
.recipe-card-content--linked {
  pointer-events: none;
}
.recipe-card-content--linked .recipe-card-actions,
.recipe-card-content--linked .recipe-card-tags {
  pointer-events: auto;
  position: relative;
  z-index: 2;
}
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

.disable-highlight :deep(.v-card__overlay) {
  opacity: 0 !important;
}
.recipe-card-selection {
  position: absolute;
  right: 8px;
  top: 8px;
  z-index: 3;
}
.recipe-card--selected {
  outline: 3px solid rgb(var(--v-theme-info));
}
</style>
