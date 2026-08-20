<template>
  <!-- Wrap v-hover with a div to provide a proper DOM element for the transition -->
  <div>
    <v-hover
      v-slot="{ isHovering, props: hoverProps }"
      :open-delay="50"
    >
      <v-card
        v-bind="hoverProps"
        :class="['recipe-card', { 'on-hover': isHovering, 'recipe-card--selected': selected }]"
        :style="{ cursor }"
        :elevation="isHovering ? 12 : 2"
        :min-height="imageHeight + 75"
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
          @click.stop="$emit('click')"
        >
          <v-icon>
            {{ selected ? $globals.icons.checkboxMarkedCircle : $globals.icons.checkboxBlankCircleOutline }}
          </v-icon>
        </v-btn>
        <div
          class="recipe-card-content"
          :class="{ 'recipe-card-content--linked': !selectMode && recipeRoute }"
        >
          <RecipeCardImage
            small
            :icon-size="imageHeight"
            :height="imageHeight"
            :slug="slug"
            :recipe-id="recipeId"
            :image-version="image"
          >
            <v-expand-transition v-if="description">
              <div
                v-if="isHovering"
                class="d-flex transition-fast-in-fast-out bg-secondary v-card--reveal"
                style="height: 100%"
              >
                <v-card-text class="v-card--text-show white--text">
                  <div class="descriptionWrapper">
                    <SafeMarkdown :source="description" />
                  </div>
                </v-card-text>
              </div>
            </v-expand-transition>
          </RecipeCardImage>
          <v-card-title class="mb-n3 px-4" style="font-size: 1.25rem;">
            {{ name }}
          </v-card-title>

          <div
            class="recipe-card-footer"
            :class="{ 'recipe-card-footer--no-tags': tags.length === 0 }"
          >
            <RecipeChips
              v-if="tags.length > 0"
              class="recipe-card-tags px-4"
              :truncate="false"
              :items="tags"
              :title="false"
              :limit="2"
              small
              url-prefix="tags"
              v-bind="$attrs"
            />

            <slot name="actions">
              <v-card-actions
                v-if="showRecipeContent"
                class="recipe-card-actions px-1 py-0"
              >
                <RecipeFavoriteBadge
                  v-if="isOwnGroup"
                  :recipe-id="recipeId"
                  show-always
                />
                <div v-else class="px-1" /> <!-- Empty div to keep the layout consistent -->

                <RecipeCardRating
                  :model-value="rating"
                  :recipe-id="recipeId"
                />
                <v-spacer />
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
                <RecipeContextMenu
                  v-if="isOwnGroup && showRecipeContent"
                  color="grey-darken-2"
                  :slug="slug"
                  :menu-icon="$globals.icons.dotsVertical"
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
              </v-card-actions>
            </slot>
          </div>
          <slot />
        </div>
      </v-card>
    </v-hover>
  </div>
</template>

<script setup lang="ts">
import RecipeFavoriteBadge from "./RecipeFavoriteBadge.vue";
import RecipeChips from "./RecipeChips.vue";
import RecipeContextMenu from "./RecipeContextMenu/RecipeContextMenu.vue";
import RecipeCardImage from "./RecipeCardImage.vue";
import RecipeCardRating from "./RecipeCardRating.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";

interface Props {
  name: string;
  slug: string;
  description?: string | null;
  rating?: number;
  ratingColor?: string;
  image?: string;
  tags?: Array<any>;
  recipeId: string;
  imageHeight?: number;
  showOrganizer?: boolean;
  selectMode?: boolean;
  selected?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  description: null,
  rating: 0,
  ratingColor: "secondary",
  image: "abc123",
  tags: () => [],
  imageHeight: 200,
  showOrganizer: false,
  selectMode: false,
  selected: false,
});

const emit = defineEmits<{
  click: [];
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
  emit("click");
}
</script>

<style>
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
.descriptionWrapper {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 8;
  line-clamp: 8;
  overflow: hidden;
}
.recipe-card-footer {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  min-height: 84px;
}
.recipe-card-footer--no-tags {
  justify-content: center;
}
.recipe-card-tags {
  display: flex;
  flex-wrap: nowrap;
  gap: 4px;
  min-width: 0;
  overflow: hidden;
}
.recipe-card-tags .v-chip {
  flex: 0 1 auto;
  margin: 0 !important;
}
.recipe-card-tags .v-chip__content {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.recipe-card-actions {
  width: 100%;
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
