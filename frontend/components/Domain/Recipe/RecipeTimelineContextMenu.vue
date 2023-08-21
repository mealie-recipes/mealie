<template>
  <div class="text-center">
    <BaseDialog
      v-model="recipeEventEditDialog"
      :title="$tc('recipe.edit-timeline-event')"
      :icon="$globals.icons.edit"
      :submit-text="$tc('general.save')"
      @submit="$emit('update')"
    >
    <v-card-text>
      <v-form ref="domMadeThisForm">
        <v-text-field
          v-model="event.subject"
          :label="$tc('general.subject')"
        />
        <v-textarea
          v-model="event.eventMessage"
          :label="$tc('general.message')"
          rows="4"
        />
      </v-form>
    </v-card-text>
    </BaseDialog>
    <BaseDialog
      v-model="recipeEventDeleteDialog"
      :title="$tc('events.delete-event')"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="$emit('delete')"
    >
      <v-card-text>
        {{ $t("events.event-delete-confirmation") }}
      </v-card-text>
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
      :open-on-hover="!useMobileFormat"
      content-class="d-print-none"
    >
      <template #activator="{ on, attrs }">
        <v-btn :fab="fab" :x-small="fab" :elevation="elevation" :color="color" :icon="!fab" v-bind="attrs" v-on="on" @click.prevent>
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
import { defineComponent, reactive, ref, toRefs, useContext } from "@nuxtjs/composition-api";
import { VForm } from "~/types/vuetify";
import { RecipeTimelineEventOut } from "~/lib/api/types/recipe";

export interface TimelineContextMenuIncludes {
  edit: boolean;
  delete: boolean;
}

export interface ContextMenuItem {
  title: string;
  icon: string;
  color: string | undefined;
  event: string;
}

export default defineComponent({
  props: {
    useItems: {
      type: Object as () => TimelineContextMenuIncludes,
      default: () => ({
        edit: true,
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
    elevation: {
      type: Number,
      default: null
    },
    color: {
      type: String,
      default: "primary",
    },
    event: {
      type: Object as () => RecipeTimelineEventOut,
      required: true,
    },
    menuIcon: {
      type: String,
      default: null,
    },
    useMobileFormat: {
      type: Boolean,
      default: true,
    }
  },
  setup(props, context) {
    const domEditEventForm = ref<VForm>();
    const state = reactive({
      recipeEventEditDialog: false,
      recipeEventDeleteDialog: false,
      loading: false,
      menuItems: [] as ContextMenuItem[],
    });

    const { i18n, $globals } = useContext();

    // ===========================================================================
    // Context Menu Setup

    const defaultItems: { [key: string]: ContextMenuItem } = {
      edit: {
        title: i18n.tc("general.edit"),
        icon: $globals.icons.edit,
        color: undefined,
        event: "edit",
      },
      delete: {
        title: i18n.tc("general.delete"),
        icon: $globals.icons.delete,
        color: "error",
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

    // Add Leading and Appending Items
    state.menuItems = [...state.menuItems, ...props.leadingItems, ...props.appendItems];

    const icon = props.menuIcon || $globals.icons.dotsVertical;

    // ===========================================================================
    // Context Menu Event Handler

    const eventHandlers: { [key: string]: () => void | Promise<any> } = {
      edit: () => {
        state.recipeEventEditDialog = true;
      },
      delete: () => {
        state.recipeEventDeleteDialog = true;
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
      domEditEventForm,
      icon,
    };
  },
});
</script>
