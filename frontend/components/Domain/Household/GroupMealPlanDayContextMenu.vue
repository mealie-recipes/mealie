<template>
  <div class="text-center">
    <RecipeDialogAddToShoppingList
      v-if="shoppingLists"
      v-model="shoppingListDialog"
      :recipes="recipesWithScales"
      :shopping-lists="shoppingLists"
    />
    <v-menu
      offset-y
      start
      :bottom="!menuTop"
      :nudge-bottom="!menuTop ? '5' : '0'"
      :top="menuTop"
      :nudge-top="menuTop ? '5' : '0'"
      allow-overflow
      close-delay="125"
      content-class="d-print-none"
    >
      <template #activator="{ props: activatorProps }">
        <v-btn
          :class="{ 'rounded-circle': fab }"
          :size="fab ? 'small' : undefined"
          :color="color"
          :icon="!fab"
          variant="text"
          dark
          v-bind="activatorProps"
          @click.prevent
        >
          <v-icon>{{ icon }}</v-icon>
        </v-btn>
      </template>
      <v-list density="compact">
        <v-list-item
          v-for="(item, index) in menuItems"
          :key="index"
          @click="contextMenuEventHandler(item.event)"
        >
          <template #prepend>
            <v-icon :color="item.color">
              {{ item.icon }}
            </v-icon>
          </template>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script setup lang="ts">
import type { Recipe } from "~/lib/api/types/recipe";
import RecipeDialogAddToShoppingList from "~/components/Domain/Recipe/RecipeDialogAddToShoppingList.vue";
import type { ShoppingListSummary } from "~/lib/api/types/household";
import { useUserApi } from "~/composables/api";

export interface ContextMenuItem {
  title: string;
  icon: string;
  color: string | undefined;
  event: string;
  isPublic: boolean;
}

interface Props {
  recipes?: Recipe[];
  menuTop?: boolean;
  fab?: boolean;
  color?: string;
  menuIcon?: string | null;
}
const props = withDefaults(defineProps<Props>(), {
  recipes: () => [],
  menuTop: true,
  fab: false,
  color: "primary",
  menuIcon: null,
});

const emit = defineEmits<{
  [key: string]: [];
}>();

const i18n = useI18n();
const { $globals } = useNuxtApp();
const api = useUserApi();

const state = reactive({
  loading: false,
  shoppingListDialog: false,
  menuItems: [
    {
      title: i18n.t("recipe.add-to-list"),
      icon: $globals.icons.cartCheck,
      color: undefined,
      event: "shoppingList",
      isPublic: false,
    },
  ],
});

const { shoppingListDialog, menuItems } = toRefs(state);

const icon = props.menuIcon || $globals.icons.dotsVertical;

const shoppingLists = ref<ShoppingListSummary[]>();
const recipesWithScales = computed(() => {
  return props.recipes.map((recipe) => {
    return {
      scale: 1,
      ...recipe,
    };
  });
});

async function getShoppingLists() {
  const { data } = await api.shopping.lists.getAll(1, -1, { orderBy: "name", orderDirection: "asc" });
  if (data) {
    shoppingLists.value = data.items as ShoppingListSummary[] ?? [];
  }
}

// eslint-disable-next-line @typescript-eslint/no-invalid-void-type
const eventHandlers: { [key: string]: () => void | Promise<any> } = {
  shoppingList: () => {
    getShoppingLists();
    state.shoppingListDialog = true;
  },
};

function contextMenuEventHandler(eventKey: string) {
  const handler = eventHandlers[eventKey];

  if (handler && typeof handler === "function") {
    handler();
    state.loading = false;
    return;
  }

  emit(eventKey);
  state.loading = false;
}
</script>
