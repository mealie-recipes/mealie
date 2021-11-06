<template>
  <div class="text-center">
    <BaseDialog
      ref="domConfirmDelete"
      :title="$t('recipe.delete-recipe')"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="deleteRecipe()"
    >
      <v-card-text>
        {{ $t("recipe.delete-confirmation") }}
      </v-card-text>
    </BaseDialog>
    <BaseDialog
      ref="domMealplanDialog"
      title="Add Recipe to Mealplan"
      color="primary"
      :icon="$globals.icons.calendar"
      @confirm="addRecipeToPlan()"
    >
      <v-card-text>
        <v-menu
          v-model="pickerMenu"
          :close-on-content-click="false"
          transition="scale-transition"
          offset-y
          max-width="290px"
          min-width="auto"
        >
          <template #activator="{ on, attrs }">
            <v-text-field
              v-model="newMealdate"
              label="Date"
              hint="MM/DD/YYYY format"
              persistent-hint
              :prepend-icon="$globals.icons.calendar"
              v-bind="attrs"
              readonly
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker v-model="newMealdate" no-title @input="pickerMenu = false"></v-date-picker>
        </v-menu>
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
import { defineComponent, reactive, ref, toRefs, useContext, useRouter } from "@nuxtjs/composition-api";
import { useClipboard, useShare } from "@vueuse/core";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";

export interface ContextMenuIncludes {
  delete: boolean;
  edit: boolean;
  download: boolean;
  mealplanner: boolean;
  print: boolean;
  share: boolean;
}

export interface ContextMenuItem {
  title: string;
  icon: string;
  color: string;
  event: string;
}

export default defineComponent({
  props: {
    useItems: {
      type: Object as () => ContextMenuIncludes,
      default: () => ({
        delete: true,
        edit: true,
        download: true,
        mealplanner: true,
        print: true,
        share: true,
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
      default: "primary",
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
    recipeId: {
      required: true,
      type: Number,
    },
  },
  setup(props, context) {
    const api = useUserApi();

    const state = reactive({
      loading: false,
      menuItems: [] as ContextMenuItem[],
      newMealdate: "",
      pickerMenu: false,
    });

    // @ts-ignore
    const { i18n, $globals } = useContext();

    // ===========================================================================
    // Context Menu Setup

    const defaultItems: { [key: string]: ContextMenuItem } = {
      edit: {
        title: i18n.t("general.edit") as string,
        icon: $globals.icons.edit,
        color: "primary",
        event: "edit",
      },
      delete: {
        title: i18n.t("general.delete") as string,
        icon: $globals.icons.delete,
        color: "error",
        event: "delete",
      },
      download: {
        title: i18n.t("general.download") as string,
        icon: $globals.icons.download,
        color: "primary",
        event: "download",
      },
      mealplanner: {
        title: "Add to Plan",
        icon: $globals.icons.calendar,
        color: "primary",
        event: "mealplanner",
      },
      print: {
        title: i18n.t("general.print") as string,
        icon: $globals.icons.printer,
        color: "primary",
        event: "print",
      },
      share: {
        title: i18n.t("general.share") as string,
        icon: $globals.icons.shareVariant,
        color: "primary",
        event: "share",
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
    state.menuItems = [...state.menuItems, ...props.leadingItems, ...props.appendItems];

    const icon = props.menuIcon || $globals.icons.dotsVertical;

    function getRecipeUrl() {
      return `${window.location.origin}/recipe/${props.slug}`;
    }

    function getRecipeText() {
      return i18n.t("recipe.share-recipe-message", [props.name]);
    }

    // ===========================================================================
    // Context Menu Event Handler

    const router = useRouter();

    const domConfirmDelete = ref(null);

    async function deleteRecipe() {
      await api.recipes.deleteOne(props.slug);
      context.emit("delete", props.slug);
    }

    async function handleDownloadEvent() {
      const { data } = await api.recipes.getZipToken(props.slug);

      if (data) {
        window.open(api.recipes.getZipRedirectUrl(props.slug, data.token));
      }
    }

    const { share, isSupported: shareIsSupported } = useShare();

    const { copy } = useClipboard();

    async function handleShareEvent() {
      if (shareIsSupported) {
        share({
          title: props.name,
          url: getRecipeUrl(),
          text: getRecipeText() as string,
        });
      } else {
        await copy(getRecipeUrl());
        alert.success("Recipe link copied to clipboard");
      }
    }

    const domMealplanDialog = ref(null);
    async function addRecipeToPlan() {
      const { response } = await api.mealplans.createOne({
        date: state.newMealdate,
        entryType: "dinner",
        title: "",
        text: "",
        recipeId: props.recipeId,
      });

      if (response?.status === 201) {
        alert.success("Recipe added to mealplan");
      } else {
        alert.error("Failed to add recipe to mealplan");
      }
    }

    // Note: Print is handled as an event in the parent component
    const eventHandlers: { [key: string]: Function } = {
      // @ts-ignore - Doens't know about open()
      delete: () => domConfirmDelete?.value?.open(),
      edit: () => router.push(`/recipe/${props.slug}` + "?edit=true"),
      download: handleDownloadEvent,
      // @ts-ignore - Doens't know about open()
      mealplanner: () => domMealplanDialog?.value?.open(),
      share: handleShareEvent,
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
      deleteRecipe,
      addRecipeToPlan,
      domConfirmDelete,
      domMealplanDialog,
      icon,
    };
  },
});
</script>
