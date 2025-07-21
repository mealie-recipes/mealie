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
      can-confirm
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
      can-confirm
      @confirm="duplicateRecipe()"
    >
      <v-card-text>
        <v-text-field
          v-model="recipeName"
          density="compact"
          :label="$t('recipe.recipe-name')"
          autofocus
          @keyup.enter="duplicateRecipe()"
        />
      </v-card-text>
    </BaseDialog>
    <BaseDialog
      v-model="mealplannerDialog"
      :title="$t('recipe.add-recipe-to-mealplan')"
      color="primary"
      :icon="$globals.icons.calendar"
      can-confirm
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
          <template #activator="{ props }">
            <v-text-field
              v-model="newMealdateString"
              :label="$t('general.date')"
              :prepend-icon="$globals.icons.calendar"
              v-bind="props"
              readonly
            />
          </template>
          <v-date-picker
            v-model="newMealdate"
            hide-header
            :first-day-of-week="firstDayOfWeek"
            :local="$i18n.locale"
             @update:model-value="pickerMenu = false"
          />
        </v-menu>
        <v-select
          v-model="newMealType"
          :return-object="false"
          :items="planTypeOptions"
          :label="$t('recipe.entry-type')"
          item-title="text"
          item-value="value"
        />
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
      start
      :bottom="!menuTop"
      :nudge-bottom="!menuTop ? '5' : '0'"
      :top="menuTop"
      :nudge-top="menuTop ? '5' : '0'"
      allow-overflow
      close-delay="125"
      :open-on-hover="$vuetify.display.mdAndUp"
      content-class="d-print-none"
    >
      <template #activator="{ props }">
        <v-btn
          icon
          :variant="fab ? 'flat' : undefined"
          :rounded="fab ? 'circle' : undefined"
          :size="fab ? 'small' : undefined"
          :color="fab ? 'info' : 'secondary'"
          :fab="fab"
          v-bind="props"
          @click.prevent
        >
          <v-icon
          :size="!fab ? undefined : 'x-large'"
          :color="fab ? 'white' : 'secondary'"
        >
          {{ icon }}
        </v-icon>
        </v-btn>
      </template>
      <v-list density="compact">
        <v-list-item v-for="(item, index) in menuItems" :key="index" @click="contextMenuEventHandler(item.event)">
          <template #prepend>
            <v-icon :color="item.color">
              {{ item.icon }}
            </v-icon>
          </template>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
        <div v-if="useItems.recipeActions && recipeActions && recipeActions.length">
          <v-divider />
          <v-list-item
            v-for="(action, index) in recipeActions"
            :key="index"
            @click="executeRecipeAction(action)"
          >
            <template #prepend>
              <v-icon color="undefined">
                {{ $globals.icons.linkVariantPlus }}
              </v-icon>
            </template>
            <v-list-item-title>
              {{ action.title }}
            </v-list-item-title>
          </v-list-item>
        </div>
      </v-list>
    </v-menu>
  </div>
</template>

<script lang="ts">
import RecipeDialogAddToShoppingList from "./RecipeDialogAddToShoppingList.vue";
import RecipeDialogPrintPreferences from "./RecipeDialogPrintPreferences.vue";
import RecipeDialogShare from "./RecipeDialogShare.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserApi } from "~/composables/api";
import { useGroupRecipeActions } from "~/composables/use-group-recipe-actions";
import { useHouseholdSelf } from "~/composables/use-households";
import { alert } from "~/composables/use-toast";
import { usePlanTypeOptions } from "~/composables/use-group-mealplan";
import type { Recipe } from "~/lib/api/types/recipe";
import type { GroupRecipeActionOut, ShoppingListSummary } from "~/lib/api/types/household";
import type { PlanEntryType } from "~/lib/api/types/meal-plan";
import { useDownloader } from "~/composables/api/use-downloader";

export interface ContextMenuIncludes {
  delete: boolean;
  edit: boolean;
  download: boolean;
  duplicate: boolean;
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

export default defineNuxtComponent({
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
  emits: ["delete"],
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
      newMealdate: new Date(),
      newMealType: "dinner" as PlanEntryType,
      pickerMenu: false,
    });

    const newMealdateString = computed(() => {
      // Format the date to YYYY-MM-DD in the same timezone as newMealdate
      const year = state.newMealdate.getFullYear();
      const month = String(state.newMealdate.getMonth() + 1).padStart(2, "0");
      const day = String(state.newMealdate.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    });

    const i18n = useI18n();
    const $auth = useMealieAuth();
    const { $globals } = useNuxtApp();
    const { household } = useHouseholdSelf();
    const { isOwnGroup } = useLoggedInState();

    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug || $auth.user.value?.groupSlug || "");

    const firstDayOfWeek = computed(() => {
      return household.value?.preferences?.firstDayOfWeek || 0;
    });

    // ===========================================================================
    // Context Menu Setup

    const defaultItems: { [key: string]: ContextMenuItem } = {
      edit: {
        title: i18n.t("general.edit"),
        icon: $globals.icons.edit,
        color: undefined,
        event: "edit",
        isPublic: false,
      },
      delete: {
        title: i18n.t("general.delete"),
        icon: $globals.icons.delete,
        color: undefined,
        event: "delete",
        isPublic: false,
      },
      download: {
        title: i18n.t("general.download"),
        icon: $globals.icons.download,
        color: undefined,
        event: "download",
        isPublic: false,
      },
      duplicate: {
        title: i18n.t("general.duplicate"),
        icon: $globals.icons.duplicate,
        color: undefined,
        event: "duplicate",
        isPublic: false,
      },
      mealplanner: {
        title: i18n.t("recipe.add-to-plan"),
        icon: $globals.icons.calendar,
        color: undefined,
        event: "mealplanner",
        isPublic: false,
      },
      shoppingList: {
        title: i18n.t("recipe.add-to-list"),
        icon: $globals.icons.cartCheck,
        color: undefined,
        event: "shoppingList",
        isPublic: false,
      },
      print: {
        title: i18n.t("general.print"),
        icon: $globals.icons.printer,
        color: undefined,
        event: "print",
        isPublic: true,
      },
      printPreferences: {
        title: i18n.t("general.print-preferences"),
        icon: $globals.icons.printerSettings,
        color: undefined,
        event: "printPreferences",
        isPublic: true,
      },
      share: {
        title: i18n.t("general.share"),
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
    const recipeRef = ref<Recipe | undefined>(props.recipe);
    const recipeRefWithScale = computed(() =>
      recipeRef.value ? { scale: props.recipeScale, ...recipeRef.value } : undefined,
    );

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
      if (!props.recipe) return;
      const response = await groupRecipeActionsStore.execute(action, props.recipe, props.recipeScale);

      if (action.actionType === "post") {
        if (!response?.error) {
          alert.success(i18n.t("events.message-sent"));
        }
        else {
          alert.error(i18n.t("events.something-went-wrong"));
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

    const download = useDownloader();

    async function handleDownloadEvent() {
      const { data } = await api.recipes.getZipToken(props.slug);

      if (data) {
        download(api.recipes.getZipRedirectUrl(props.slug, data.token), `${props.slug}.zip`);
      }
    }

    async function addRecipeToPlan() {
      const { response } = await api.mealplans.createOne({
        date: newMealdateString.value,
        entryType: state.newMealType,
        title: "",
        text: "",
        recipeId: props.recipeId,
      });

      if (response?.status === 201) {
        alert.success(i18n.t("recipe.recipe-added-to-mealplan") as string);
      }
      else {
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
    // eslint-disable-next-line @typescript-eslint/no-invalid-void-type
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

        Promise.allSettled(promises).then(() => {
          state.shoppingListDialog = true;
        });
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
      newMealdateString,
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
