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
      left
      :bottom="!menuTop"
      :nudge-bottom="!menuTop ? '5' : '0'"
      :top="menuTop"
      :nudge-top="menuTop ? '5' : '0'"
      allow-overflow
      close-delay="125"
      :open-on-hover="$vuetify.breakpoint.mdAndUp"
      content-class="d-print-none"
    >
      <template #activator="{ on, attrs }">
        <v-btn :fab="fab" :small="fab" :color="color" :icon="!fab" dark v-bind="attrs" v-on="on" @click.prevent>
          <v-icon>{{ icon }}</v-icon>
        </v-btn>
      </template>
      <v-list dense>
        <v-list-item v-for="(item, index) in menuItems" :key="index" @click="contextMenuEventHandler(item.event)">
          <v-list-item-icon>
            <v-icon :color="item.color"> {{ item.icon }} </v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, useContext } from "@nuxtjs/composition-api";
import { Recipe } from "~/lib/api/types/recipe";
import RecipeDialogAddToShoppingList from "~/components/Domain/Recipe/RecipeDialogAddToShoppingList.vue";
import { ShoppingListSummary } from "~/lib/api/types/household";
import { useUserApi } from "~/composables/api";

export interface ContextMenuItem {
  title: string;
  icon: string;
  color: string | undefined;
  event: string;
  isPublic: boolean;
}

export default defineComponent({
  components: {
    RecipeDialogAddToShoppingList,
  },
  props: {
    recipes: {
      type: Array as () => Recipe[],
      default: () => [],
    },
    menuTop: {
      type: Boolean,
      default: true,
    },
    fab: {
      type: Boolean,
      default: false,
    },
    color: {
      type: String,
      default: "primary",
    },
    menuIcon: {
      type: String,
      default: null,
    },
  },
  setup(props, context) {
    const { $globals, i18n } = useContext();
    const api = useUserApi();

    const state = reactive({
      loading: false,
      shoppingListDialog: false,
      menuItems: [
        {
          title: i18n.tc("recipe.add-to-list"),
          icon: $globals.icons.cartCheck,
          color: undefined,
          event: "shoppingList",
          isPublic: false,
        },
      ],
    });

    const icon = props.menuIcon || $globals.icons.dotsVertical;

    const shoppingLists = ref<ShoppingListSummary[]>();
    const recipesWithScales = computed(() => {
      return props.recipes.map((recipe) => {
        return {
          scale: 1,
          ...recipe,
        };
      })
    })

    async function getShoppingLists() {
      const { data } = await api.shopping.lists.getAll(1, -1, { orderBy: "name", orderDirection: "asc" });
      if (data) {
        shoppingLists.value = data.items ?? [];
      }
    }

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

      context.emit(eventKey);
      state.loading = false;
    }

    return {
      ...toRefs(state),
      contextMenuEventHandler,
      icon,
      recipesWithScales,
      shoppingLists,
    }
  },
})
</script>
