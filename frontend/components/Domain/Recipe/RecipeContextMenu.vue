<template>
  <div class="text-center">
    <!-- Recipe Share Dialog -->
    <RecipeDialogShare v-model="shareDialog" :recipe-id="recipeId" :name="name" />
    <RecipeDialogPrintPreferences v-model="printPreferencesDialog" :recipe="recipeRef" />
    <BaseDialog
      v-model="recipeDeleteDialog"
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
      v-model="recipeDuplicateDialog"
      :title="$t('recipe.duplicate')"
      color="primary"
      :icon="$globals.icons.duplicate"
      @confirm="duplicateRecipe()"
    >
      <v-card-text>
        <v-text-field
          v-model="recipeName"
          dense
          :label="$t('recipe.recipe-name')"
          autofocus
          @keyup.enter="duplicateRecipe()"
        ></v-text-field>
      </v-card-text>
    </BaseDialog>
    <BaseDialog
      v-model="mealplannerDialog"
      :title="$t('recipe.add-recipe-to-mealplan')"
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
              :label="$t('general.date')"
              :prepend-icon="$globals.icons.calendar"
              v-bind="attrs"
              readonly
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker
            v-model="newMealdate"
            no-title
            :first-day-of-week="firstDayOfWeek"
            :local="$i18n.locale"
            @input="pickerMenu = false"
          />
        </v-menu>
        <v-select
          v-model="newMealType"
          :return-object="false"
          :items="planTypeOptions"
          :label="$t('recipe.entry-type')"
        ></v-select>
      </v-card-text>
    </BaseDialog>
    <RecipeDialogAddToShoppingList
      v-if="shoppingLists && recipeRefWithScale"
      v-model="shoppingListDialog"
      :recipes="[recipeRefWithScale]"
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
        <div v-if="useItems.recipeActions && recipeActions && recipeActions.length">
          <v-divider />
          <v-list-group @click.stop>
            <template #activator>
              <v-list-item-title>{{ $tc("recipe.recipe-actions") }}</v-list-item-title>
            </template>
            <v-list dense class="ma-0 pa-0">
              <v-list-item
                v-for="(action, index) in recipeActions"
                :key="index"
                class="pl-6"
                @click="executeRecipeAction(action)"
              >
                <v-list-item-title>
                  {{ action.title }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-list-group>
        </div>
      </v-list>
    </v-menu>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, useContext, useRoute, useRouter, ref } from "@nuxtjs/composition-api";
import RecipeDialogAddToShoppingList from "./RecipeDialogAddToShoppingList.vue";
import RecipeDialogPrintPreferences from "./RecipeDialogPrintPreferences.vue";
import RecipeDialogShare from "./RecipeDialogShare.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserApi } from "~/composables/api";
import { useGroupRecipeActions } from "~/composables/use-group-recipe-actions";
import { useHouseholdSelf } from "~/composables/use-households";
import { alert } from "~/composables/use-toast";
import { usePlanTypeOptions } from "~/composables/use-group-mealplan";
import { Recipe } from "~/lib/api/types/recipe";
import { GroupRecipeActionOut, ShoppingListSummary } from "~/lib/api/types/household";
import { PlanEntryType } from "~/lib/api/types/meal-plan";
import { useAxiosDownloader } from "~/composables/api/use-axios-download";

export interface ContextMenuIncludes {
  delete: boolean;
  edit: boolean;
  download: boolean;
  mealplanner: boolean;
  shoppingList: boolean;
  print: boolean;
  printPreferences: boolean;
  share: boolean;
  recipeActions: boolean;
}

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
    RecipeDialogPrintPreferences,
    RecipeDialogShare,
},
  props: {
    useItems: {
      type: Object as () => ContextMenuIncludes,
      default: () => ({
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
    recipe: {
      type: Object as () => Recipe,
      default: undefined,
    },
    recipeId: {
      required: true,
      type: String,
    },
    recipeScale: {
      type: Number,
      default: 1,
    },
  },
  setup(props, context) {
    const api = useUserApi();

    const state = reactive({
      printPreferencesDialog: false,
      shareDialog: false,
      recipeDeleteDialog: false,
      mealplannerDialog: false,
      shoppingListDialog: false,
      recipeDuplicateDialog: false,
      recipeName: props.name,
      loading: false,
      menuItems: [] as ContextMenuItem[],
      newMealdate: "",
      newMealType: "dinner" as PlanEntryType,
      pickerMenu: false,
    });

    const { i18n, $auth, $globals } = useContext();
    const { household } = useHouseholdSelf();
    const { isOwnGroup } = useLoggedInState();

    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

    const firstDayOfWeek = computed(() => {
      return household.value?.preferences?.firstDayOfWeek || 0;
    });

    // ===========================================================================
    // Context Menu Setup

    const defaultItems: { [key: string]: ContextMenuItem } = {
      edit: {
        title: i18n.tc("general.edit"),
        icon: $globals.icons.edit,
        color: undefined,
        event: "edit",
        isPublic: false,
      },
      delete: {
        title: i18n.tc("general.delete"),
        icon: $globals.icons.delete,
        color: undefined,
        event: "delete",
        isPublic: false,
      },
      download: {
        title: i18n.tc("general.download"),
        icon: $globals.icons.download,
        color: undefined,
        event: "download",
        isPublic: false,
      },
      duplicate: {
        title: i18n.tc("general.duplicate"),
        icon: $globals.icons.duplicate,
        color: undefined,
        event: "duplicate",
        isPublic: false,
      },
      mealplanner: {
        title: i18n.tc("recipe.add-to-plan"),
        icon: $globals.icons.calendar,
        color: undefined,
        event: "mealplanner",
        isPublic: false,
      },
      shoppingList: {
        title: i18n.tc("recipe.add-to-list"),
        icon: $globals.icons.cartCheck,
        color: undefined,
        event: "shoppingList",
        isPublic: false,
      },
      print: {
        title: i18n.tc("general.print"),
        icon: $globals.icons.printer,
        color: undefined,
        event: "print",
        isPublic: true,
      },
      printPreferences: {
        title: i18n.tc("general.print-preferences"),
        icon: $globals.icons.printerSettings,
        color: undefined,
        event: "printPreferences",
        isPublic: true,
      },
      share: {
        title: i18n.tc("general.share"),
        icon: $globals.icons.shareVariant,
        color: undefined,
        event: "share",
        isPublic: false,
      },
    };

    // Get Default Menu Items Specified in Props
    for (const [key, value] of Object.entries(props.useItems)) {
      if (value) {
        const item = defaultItems[key];
        if (item && (item.isPublic || isOwnGroup.value)) {
          state.menuItems.push(item);
        }
      }
    }

    // Add leading and Appending Items
    state.menuItems = [...state.menuItems, ...props.leadingItems, ...props.appendItems];

    const icon = props.menuIcon || $globals.icons.dotsVertical;

    // ===========================================================================
    // Context Menu Event Handler

    const shoppingLists = ref<ShoppingListSummary[]>();
    const recipeRef = ref<Recipe>(props.recipe);
    const recipeRefWithScale = computed(() => recipeRef.value ? { scale: props.recipeScale, ...recipeRef.value } : undefined);

    async function getShoppingLists() {
      const { data } = await api.shopping.lists.getAll(1, -1, { orderBy: "name", orderDirection: "asc" });
      if (data) {
        shoppingLists.value = data.items ?? [];
      }
    }

    async function refreshRecipe() {
      const { data } = await api.recipes.getOne(props.slug);
      if (data) {
        recipeRef.value = data;
      }
    }

    const router = useRouter();
    const groupRecipeActionsStore = useGroupRecipeActions();

    async function executeRecipeAction(action: GroupRecipeActionOut) {
      const response = await groupRecipeActionsStore.execute(action, props.recipe);

      if (action.actionType === "post") {
        if (!response?.error) {
          alert.success(i18n.tc("events.message-sent"));
        } else {
          alert.error(i18n.tc("events.something-went-wrong"));
        }
      }
    }

    async function deleteRecipe() {
      const { data } = await api.recipes.deleteOne(props.slug);
      if (data?.slug) {
        router.push(`/g/${groupSlug.value}`);
      }
      context.emit("delete", props.slug);
    }

    const download = useAxiosDownloader();

    async function handleDownloadEvent() {
      const { data } = await api.recipes.getZipToken(props.slug);

      if (data) {
        download(api.recipes.getZipRedirectUrl(props.slug, data.token), `${props.slug}.zip`);
      }
    }

    async function addRecipeToPlan() {
      const { response } = await api.mealplans.createOne({
        date: state.newMealdate,
        entryType: state.newMealType,
        title: "",
        text: "",
        recipeId: props.recipeId,
      });

      if (response?.status === 201) {
        alert.success(i18n.t("recipe.recipe-added-to-mealplan") as string);
      } else {
        alert.error(i18n.t("recipe.failed-to-add-recipe-to-mealplan") as string);
      }
    }

    async function duplicateRecipe() {
      const { data } = await api.recipes.duplicateOne(props.slug, state.recipeName);
      if (data && data.slug) {
        router.push(`/g/${groupSlug.value}/r/${data.slug}`);
      }
    }

    // Note: Print is handled as an event in the parent component
    const eventHandlers: { [key: string]: () => void | Promise<any> } = {
      delete: () => {
        state.recipeDeleteDialog = true;
      },
      edit: () => router.push(`/g/${groupSlug.value}/r/${props.slug}` + "?edit=true"),
      download: handleDownloadEvent,
      duplicate: () => {
        state.recipeDuplicateDialog = true;
      },
      mealplanner: () => {
        state.mealplannerDialog = true;
      },
      printPreferences: async () => {
        if (!recipeRef.value) {
          await refreshRecipe();
        }
        state.printPreferencesDialog = true;
      },
      shoppingList: () => {
        const promises: Promise<void>[] = [getShoppingLists()];
        if (!recipeRef.value) {
          promises.push(refreshRecipe());
        }

        Promise.allSettled(promises).then(() => { state.shoppingListDialog = true });
      },
      share: () => {
        state.shareDialog = true;
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

    const planTypeOptions = usePlanTypeOptions();

    return {
      ...toRefs(state),
      recipeRef,
      recipeRefWithScale,
      executeRecipeAction,
      recipeActions: groupRecipeActionsStore.recipeActions,
      shoppingLists,
      duplicateRecipe,
      contextMenuEventHandler,
      deleteRecipe,
      addRecipeToPlan,
      icon,
      planTypeOptions,
      firstDayOfWeek,
    };
  },
});
</script>
