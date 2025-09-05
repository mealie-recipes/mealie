<template>
  <div class="text-center">
    <v-menu
      offset-y
      start
      :bottom="!menuTop"
      :nudge-bottom="!menuTop ? '5' : '0'"
      :top="menuTop"
      :nudge-top="menuTop ? '5' : '0'"
      allow-overflow
      close-delay="125"
      :open-on-hover="$vuetify.display.mdAndUp"
      content-class="d-print-none"
      @update:model-value="onMenuToggle"
    >
      <template #activator="{ props: activatorProps }">
        <v-btn
          icon
          :variant="fab ? 'flat' : undefined"
          :rounded="fab ? 'circle' : undefined"
          :size="fab ? 'small' : undefined"
          :color="fab ? 'info' : 'secondary'"
          :fab="fab"
          v-bind="activatorProps"
          @click.prevent
          @mouseenter="onHover"
        >
          <v-icon
            :size="!fab ? undefined : 'x-large'"
            :color="fab ? 'white' : 'secondary'"
          >
            {{ icon }}
          </v-icon>
        </v-btn>
      </template>

      <RecipeContextMenuContent
        v-if="isMenuContentLoaded"
        v-bind="contentProps"
        @deleted="$emit('deleted', $event)"
      />
    </v-menu>
  </div>
</template>

<script setup lang="ts">
import type { Recipe } from "~/lib/api/types/recipe";

interface ContextMenuIncludes {
  delete?: boolean;
  edit?: boolean;
  download?: boolean;
  duplicate?: boolean;
  mealplanner?: boolean;
  shoppingList?: boolean;
  print?: boolean;
  printPreferences?: boolean;
  share?: boolean;
  recipeActions?: boolean;
}

interface ContextMenuItem {
  title: string;
  icon: string;
  color?: string;
  event: string;
  isPublic: boolean;
}

interface Props {
  useItems?: ContextMenuIncludes;
  appendItems?: ContextMenuItem[];
  leadingItems?: ContextMenuItem[];
  menuTop?: boolean;
  fab?: boolean;
  color?: string;
  slug: string;
  menuIcon?: string | null;
  name: string;
  recipe?: Recipe;
  recipeId: string;
  recipeScale?: number;
}

const props = withDefaults(defineProps<Props>(), {
  useItems: () => ({
    delete: true,
    edit: true,
    download: true,
    duplicate: false,
    mealplanner: true,
    shoppingList: true,
    print: true,
    printPreferences: true,
    share: true,
    recipeActions: true,
  }),
  appendItems: () => [],
  leadingItems: () => [],
  menuTop: true,
  fab: false,
  color: "primary",
  menuIcon: null,
  recipe: undefined,
  recipeScale: 1,
});

defineEmits<{
  [key: string]: any;
  deleted: [slug: string];
}>();

const { $globals } = useNuxtApp();

const isMenuContentLoaded = ref(false);

const icon = computed(() => {
  return props.menuIcon || $globals.icons.dotsVertical;
});

// Props to pass to the content component (excluding internal wrapper props)
const contentProps = computed(() => {
  const { ...rest } = props;
  return rest;
});

function onHover() {
  if (!isMenuContentLoaded.value) {
    isMenuContentLoaded.value = true;
  }
}

function onMenuToggle(isOpen: boolean) {
  if (isOpen && !isMenuContentLoaded.value) {
    isMenuContentLoaded.value = true;
  }
}

const RecipeContextMenuContent = defineAsyncComponent(
  () => import("./RecipeContextMenuContent.vue"),
);
</script>
