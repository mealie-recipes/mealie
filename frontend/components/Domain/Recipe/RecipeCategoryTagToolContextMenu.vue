<template>
  <div class="text-center">
    <BaseDialog
      v-model="ItemDeleteDialog"
      :title="`Delete ${itemName}`"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="deleteItem()"
    >
      <v-card-text> Are you sure you want to delete this {{ itemName }}? </v-card-text>
    </BaseDialog>
    <v-menu
      offset-y
      left
      :bottom="!menuTop"
      :nudge-bottom="!menuTop ? '5' : '0'"
      :top="menuTop"
      :nudge-top="menuTop ? '5' : '0'"
      allow-overflow
      close-delay="125"
      open-on-hover
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
            <v-icon :color="item.color" v-text="item.icon"></v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, useContext } from "@nuxtjs/composition-api";
import colors from "vuetify/lib/util/colors";
import { useUserApi } from "~/composables/api";

export interface ContextMenuIncludes {
  delete: boolean;
}

export interface ContextMenuItem {
  title: string;
  icon: string;
  color: string | undefined;
  event: string;
}

const ItemTypes = {
  tag: "tags",
  category: "categories",
  tool: "tools",
};

export default defineComponent({
  props: {
    itemType: {
      type: String as () => string,
      required: true,
    },
    useItems: {
      type: Object as () => ContextMenuIncludes,
      default: () => ({
        delete: true,
      }),
    },
    // Append items are added at the end of the useItems list
    appendItems: {
      type: Array as () => ContextMenuItem[],
      default: () => [],
    },
    // Append items are added at the beginning of the useItems list
    leadingItems: {
      type: Array as () => ContextMenuItem[],
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
      default: colors.grey.darken2,
    },
    slug: {
      type: String,
      required: true,
    },
    menuIcon: {
      type: String,
      default: null,
    },
    name: {
      required: true,
      type: String,
    },
    id: {
      required: true,
      type: String,
    },
  },
  setup(props, context) {
    const api = useUserApi();

    const state = reactive({
      ItemDeleteDialog: false,
      loading: false,
      menuItems: [] as ContextMenuItem[],
      itemName: "tag",
    });

    const { i18n, $globals } = useContext();

    let apiRoute = "tags" as "tags" | "categories" | "tools";

    switch (props.itemType) {
      case ItemTypes.tag:
        state.itemName = "tag";
        apiRoute = "tags";
        break;
      case ItemTypes.category:
        state.itemName = "category";
        apiRoute = "categories";
        break;
      case ItemTypes.tool:
        state.itemName = "tool";
        apiRoute = "tools";
        break;
      default:
        break;
    }

    // ===========================================================================
    // Context Menu Setup

    const defaultItems: { [key: string]: ContextMenuItem } = {
      delete: {
        title: i18n.t("general.delete") as string,
        icon: $globals.icons.delete,
        color: undefined,
        event: "delete",
      },
    };

    // Get Default Menu Items Specified in Props
    for (const [key, value] of Object.entries(props.useItems)) {
      if (value) {
        const item = defaultItems[key];
        if (item) {
          state.menuItems.push(item);
        }
      }
    }

    // Add leading and Apppending Items
    state.menuItems = [...props.leadingItems, ...state.menuItems, ...props.appendItems];

    const icon = props.menuIcon || $globals.icons.dotsVertical;

    async function deleteItem() {
      await api[apiRoute].deleteOne(props.id);
      context.emit("delete", props.id);
    }

    // Note: Print is handled as an event in the parent component
    const eventHandlers: { [key: string]: () => void } = {
      delete: () => {
        state.ItemDeleteDialog = true;
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
      deleteItem,
      icon,
    };
  },
});
</script>
