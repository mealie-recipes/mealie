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
              :hint="$t('recipe.date-format-hint')"
              persistent-hint
              :prepend-icon="$globals.icons.calendar"
              v-bind="attrs"
              readonly
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker v-model="newMealdate" no-title @input="pickerMenu = false"></v-date-picker>
        </v-menu>
        <v-select
          v-model="newMealType"
          :return-object="false"
          :items="planTypeOptions"
          :label="$t('recipe.entry-type')"
        ></v-select>
      </v-card-text>
    </BaseDialog>
    <BaseDialog v-model="shoppingListDialog" :title="$t('recipe.add-to-list')" :icon="$globals.icons.cartCheck">
      <v-card-text>
        <v-card
          v-for="list in shoppingLists"
          :key="list.id"
          hover
          class="my-2 left-border"
          @click="openShoppingListIngredientDialog(list)"
        >
          <v-card-title class="py-2">
            {{ list.name }}
          </v-card-title>
        </v-card>
      </v-card-text>
    </BaseDialog>
    <BaseDialog
      v-model="shoppingListIngredientDialog"
      :title="selectedShoppingList ? selectedShoppingList.name : $t('recipe.add-to-list')"
      :icon="$globals.icons.cartCheck"
      width="70%"
      :submit-text="$tc('recipe.add-to-list')"
      @submit="addRecipeToList()"
    >
      <v-card
        elevation="0"
        height="fit-content"
        max-height="60vh"
        width="100%"
        :class="$vuetify.breakpoint.smAndDown ? '' : 'ingredient-grid'"
        :style="$vuetify.breakpoint.smAndDown ? '' : { gridTemplateRows: `repeat(${Math.ceil(recipeIngredients.length / 2)}, min-content)` }"
        style="overflow-y: auto"
      >
        <v-list-item
          v-for="(ingredientData, i) in recipeIngredients"
          :key="'ingredient' + i"
          dense
          @click="recipeIngredients[i].checked = !recipeIngredients[i].checked"
        >
          <v-checkbox
            hide-details
            :input-value="ingredientData.checked"
            class="pt-0 my-auto py-auto"
            color="secondary"
          />
          <v-list-item-content :key="ingredientData.ingredient.quantity">
            <RecipeIngredientListItem
              :ingredient="ingredientData.ingredient"
              :disable-amount="ingredientData.disableAmount"
              :scale="recipeScale" />
          </v-list-item-content>
        </v-list-item>
      </v-card>
      <div class="d-flex justify-end mb-4 mt-2">
        <BaseButtonGroup
          :buttons="[
            {
              icon: $globals.icons.checkboxBlankOutline,
              text: $tc('shopping-list.uncheck-all-items'),
              event: 'uncheck',
            },
            {
              icon: $globals.icons.checkboxOutline,
              text: $tc('shopping-list.check-all-items'),
              event: 'check',
            },
          ]"
          @uncheck="bulkCheckIngredients(false)"
          @check="bulkCheckIngredients(true)"
        />
      </div>
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
import { defineComponent, reactive, toRefs, useContext, useRouter, ref } from "@nuxtjs/composition-api";
import RecipeIngredientListItem from "./RecipeIngredientListItem.vue";
import RecipeDialogPrintPreferences from "./RecipeDialogPrintPreferences.vue";
import RecipeDialogShare from "./RecipeDialogShare.vue";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { usePlanTypeOptions } from "~/composables/use-group-mealplan";
import { Recipe, RecipeIngredient } from "~/lib/api/types/recipe";
import { ShoppingListSummary } from "~/lib/api/types/group";
import { PlanEntryType } from "~/lib/api/types/meal-plan";
import { useAxiosDownloader } from "~/composables/api/use-axios-download";
import { useCopy } from "~/composables/use-copy";

export interface ContextMenuIncludes {
  delete: boolean;
  edit: boolean;
  download: boolean;
  mealplanner: boolean;
  shoppingList: boolean;
  print: boolean;
  printPreferences: boolean;
  share: boolean;
  publicUrl: boolean;
}

export interface ContextMenuItem {
  title: string;
  icon: string;
  color: string | undefined;
  event: string;
}

export default defineComponent({
  components: {
    RecipeDialogPrintPreferences,
    RecipeDialogShare,
    RecipeIngredientListItem
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
        publicUrl: false,
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
    /**
     * Optional group ID prop that is only _required_ when the
     * public URL is requested. If the public URL button is pressed
     * and the groupId is not set, an error will be thrown.
     */
    groupId: {
      type: String,
      default: "",
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
      shoppingListIngredientDialog: false,
      recipeDuplicateDialog: false,
      recipeName: props.name,
      loading: false,
      menuItems: [] as ContextMenuItem[],
      newMealdate: "",
      newMealType: "dinner" as PlanEntryType,
      pickerMenu: false,
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
      download: {
        title: i18n.tc("general.download"),
        icon: $globals.icons.download,
        color: undefined,
        event: "download",
      },
      duplicate: {
        title: i18n.tc("general.duplicate"),
        icon: $globals.icons.duplicate,
        color: undefined,
        event: "duplicate",
      },
      mealplanner: {
        title: i18n.tc("recipe.add-to-plan"),
        icon: $globals.icons.calendar,
        color: undefined,
        event: "mealplanner",
      },
      shoppingList: {
        title: i18n.tc("recipe.add-to-list"),
        icon: $globals.icons.cartCheck,
        color: undefined,
        event: "shoppingList",
      },
      print: {
        title: i18n.tc("general.print"),
        icon: $globals.icons.printer,
        color: undefined,
        event: "print",
      },
      printPreferences: {
        title: i18n.tc("general.print-preferences"),
        icon: $globals.icons.printerSettings,
        color: undefined,
        event: "printPreferences",
      },
      share: {
        title: i18n.tc("general.share"),
        icon: $globals.icons.shareVariant,
        color: undefined,
        event: "share",
      },
      publicUrl: {
        title: i18n.tc("recipe.public-link"),
        icon: $globals.icons.contentCopy,
        color: undefined,
        event: "publicUrl",
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

    // ===========================================================================
    // Context Menu Event Handler

    const shoppingLists = ref<ShoppingListSummary[]>();
    const selectedShoppingList = ref<ShoppingListSummary>();
    const recipeRef = ref<Recipe>(props.recipe);
    const recipeIngredients = ref<{ checked: boolean; ingredient: RecipeIngredient, disableAmount: boolean }[]>([]);

    async function getShoppingLists() {
      const { data } = await api.shopping.lists.getAll();
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

    async function openShoppingListIngredientDialog(list: ShoppingListSummary) {
      selectedShoppingList.value = list;
      if (!recipeRef.value) {
        await refreshRecipe();
      }

      if (recipeRef.value?.recipeIngredient) {
        recipeIngredients.value = recipeRef.value.recipeIngredient.map((ingredient) => {
          return {
            checked: true,
            ingredient,
            disableAmount: recipeRef.value.settings?.disableAmount || false
          };
        });
      }

      state.shoppingListDialog = false;
      state.shoppingListIngredientDialog = true;
    }

    function bulkCheckIngredients(value = true) {
      recipeIngredients.value.forEach((data) => {
        data.checked = value;
      });
    }

    async function addRecipeToList() {
      if (!selectedShoppingList.value) {
        return;
      }

      const ingredients: RecipeIngredient[] = [];
      recipeIngredients.value.forEach((data) => {
        if (data.checked) {
          ingredients.push(data.ingredient);
        }
      });

      if (!ingredients.length) {
        return;
      }

      const { data } = await api.shopping.lists.addRecipe(
        selectedShoppingList.value.id,
        props.recipeId,
        props.recipeScale,
        ingredients
      );
      if (data) {
        alert.success(i18n.t("recipe.recipe-added-to-list") as string);
        state.shoppingListDialog = false;
        state.shoppingListIngredientDialog = false;
      }
    }

    const router = useRouter();

    async function deleteRecipe() {
      await api.recipes.deleteOne(props.slug);
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
        router.push(`/recipe/${data.slug}`);
      }
    }

    const { copyText } = useCopy();
    const groupSlug = ref<string>("");

    async function setGroupSlug() {
      if (!props.groupId) {
        groupSlug.value = props.groupId;
        return;
      }

      const {data} = await api.groups.getOne(props.groupId);
      if (!data) {
        groupSlug.value = props.groupId;
        return;
      }

      groupSlug.value = data.slug;
    }

    // Note: Print is handled as an event in the parent component
    const eventHandlers: { [key: string]: () => void | Promise<any> } = {
      delete: () => {
        state.recipeDeleteDialog = true;
      },
      edit: () => router.push(`/recipe/${props.slug}` + "?edit=true"),
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
        getShoppingLists();

        state.shoppingListDialog = true;
        state.shoppingListIngredientDialog = false;
      },
      share: () => {
        state.shareDialog = true;
      },
      publicUrl: async () => {
        if (!props.groupId) {
          alert.error("Unknown group ID");
          console.error("prop `groupId` is required when requesting a public URL");
          return;
        }

        if (!groupSlug.value) {
          await setGroupSlug();
        }

        copyText(`${window.location.origin}/explore/recipes/${groupSlug.value}/${props.slug}`);
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
      shoppingLists,
      selectedShoppingList,
      openShoppingListIngredientDialog,
      addRecipeToList,
      bulkCheckIngredients,
      duplicateRecipe,
      contextMenuEventHandler,
      deleteRecipe,
      addRecipeToPlan,
      icon,
      planTypeOptions,
      recipeIngredients,
    };
  },
});
</script>

<style scoped lang="css">
.ingredient-grid {
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: 1fr 1fr;
  grid-gap: 0.5rem;
}
</style>
