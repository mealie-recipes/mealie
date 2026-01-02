<template>
  <v-container
    v-if="!edit"
    class="pa-0"
  >
    <v-row
      no-gutters
      class="flex-nowrap align-center"
    >
      <v-col :cols="itemLabelCols">
        <div class="d-flex align-center flex-nowrap">
          <v-checkbox
            v-model="listItem.checked"
            hide-details
            density="compact"
            class="mt-0 flex-shrink-0"
            color="null"
            @click="() => {
              listItem.checked = !listItem.checked
              $emit('checked', listItem)
            }"
          />
          <div
            class="ml-2 text-truncate"
            :class="listItem.checked ? 'strike-through' : ''"
            style="min-width: 0;"
          >
            <RecipeIngredientListItem :ingredient="listItem" />
          </div>
        </div>
      </v-col>
      <v-spacer />
      <v-col
        cols="auto"
        class="text-right"
      >
        <div
          v-if="!listItem.checked"
          style="min-width: 72px"
        >
          <v-menu
            offset-x
            start
            min-width="125px"
          >
            <template #activator="{ props }">
              <v-tooltip
                v-if="recipeList && recipeList.length"
                open-delay="200"
                transition="slide-x-reverse-transition"
                density="compact"
                location="end"
                content-class="text-caption"
              >
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    size="small"
                    variant="text"
                    class="ml-2"
                    icon
                    v-bind="tooltipProps"
                    @click="displayRecipeRefs = !displayRecipeRefs"
                  >
                    <v-icon>
                      {{ $globals.icons.potSteam }}
                    </v-icon>
                  </v-btn>
                </template>
                <span>Toggle Recipes</span>
              </v-tooltip>
              <v-btn
                size="small"
                variant="text"
                class="ml-2"
                icon
                @click="toggleEdit(true)"
              >
                <v-icon>
                  {{ $globals.icons.edit }}
                </v-icon>
              </v-btn>
              <v-btn
                size="small"
                variant="text"
                class="handle"
                icon
                v-bind="props"
              >
                <v-icon>
                  {{ $globals.icons.arrowUpDown }}
                </v-icon>
              </v-btn>
            </template>
            <v-list density="compact">
              <v-list-item
                v-for="action in contextMenu"
                :key="action.event"
                density="compact"
                @click="contextHandler(action.event)"
              >
                <v-list-item-title>
                  {{ action.text }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </v-col>
    </v-row>
    <v-row
      v-if="!listItem.checked && recipeList && recipeList.length && displayRecipeRefs"
      no-gutters
      class="mb-2"
    >
      <v-col
        cols="auto"
        style="width: 100%;"
      >
        <RecipeList
          :recipes="recipeList"
          :list-item="listItem"
          :disabled="isOffline"
          size="small"
          tile
        />
      </v-col>
    </v-row>
    <v-row
      v-if="listItem.checked"
      no-gutters
      class="mb-2"
    >
      <v-col cols="auto">
        <div class="text-caption font-weight-light font-italic">
          {{ $t("shopping-list.completed-on", {
            date: listItem.updatedAt ? $d(new Date(listItem.updatedAt)) : '',
          }) }}
        </div>
      </v-col>
    </v-row>
  </v-container>
  <div
    v-else
    class="mb-1 mt-6"
  >
    <ShoppingListItemEditor
      v-model="localListItem"
      :labels="labels"
      :units="units"
      :foods="foods"
      @save="save"
      @cancel="toggleEdit(false)"
      @delete="$emit('delete')"
    />
  </div>
</template>

<script lang="ts">
import { useOnline } from "@vueuse/core";
import RecipeIngredientListItem from "../Recipe/RecipeIngredientListItem.vue";
import ShoppingListItemEditor from "./ShoppingListItemEditor.vue";
import type { ShoppingListItemOut } from "~/lib/api/types/household";
import type { MultiPurposeLabelOut, MultiPurposeLabelSummary } from "~/lib/api/types/labels";
import type { IngredientFood, IngredientUnit, RecipeSummary } from "~/lib/api/types/recipe";
import RecipeList from "~/components/Domain/Recipe/RecipeList.vue";

interface actions {
  text: string;
  event: string;
}

export default defineNuxtComponent({
  components: { ShoppingListItemEditor, RecipeList, RecipeIngredientListItem },
  props: {
    modelValue: {
      type: Object as () => ShoppingListItemOut,
      required: true,
    },
    labels: {
      type: Array as () => MultiPurposeLabelOut[],
      required: true,
    },
    units: {
      type: Array as () => IngredientUnit[],
      required: true,
    },
    foods: {
      type: Array as () => IngredientFood[],
      required: true,
    },
    recipes: {
      type: Map<string, RecipeSummary>,
      default: undefined,
    },
  },
  emits: ["checked", "update:modelValue", "save", "delete"],
  setup(props, context) {
    const i18n = useI18n();
    const displayRecipeRefs = ref(false);
    const itemLabelCols = ref<string>(props.modelValue.checked ? "auto" : "6");
    const isOffline = computed(() => useOnline().value === false);

    const contextMenu: actions[] = [
      {
        text: i18n.t("general.edit") as string,
        event: "edit",
      },
      {
        text: i18n.t("general.delete") as string,
        event: "delete",
      },
    ];

    // copy prop value so a refresh doesn't interrupt the user
    const localListItem = ref(Object.assign({}, props.modelValue));
    const listItem = computed({
      get: () => {
        return props.modelValue;
      },
      set: (val) => {
        // keep local copy in sync
        localListItem.value = val;
        context.emit("update:modelValue", val);
      },
    });
    const edit = ref(false);
    function toggleEdit(val = !edit.value) {
      if (edit.value === val) {
        return;
      }

      if (val) {
        // update local copy of item with the current value
        localListItem.value = props.modelValue;
      }

      edit.value = val;
    }

    function contextHandler(event: string) {
      if (event === "edit") {
        toggleEdit(true);
      }
      else {
        context.emit(event);
      }
    }
    function save() {
      context.emit("save", localListItem.value);
      edit.value = false;
    }

    const updatedLabels = computed(() => {
      return props.labels.map((label) => {
        return {
          id: label.id,
          text: label.name,
        };
      });
    });

    /**
     * Gets the label for the shopping list item. Either the label assign to the item
     * or the label of the food applied.
     */
    const label = computed<MultiPurposeLabelSummary | undefined>(() => {
      if (listItem.value.label) {
        return listItem.value.label as MultiPurposeLabelSummary;
      }

      if (listItem.value.food?.label) {
        return listItem.value.food.label;
      }

      return undefined;
    });

    const recipeList = computed<RecipeSummary[]>(() => {
      const recipeList: RecipeSummary[] = [];
      if (!listItem.value.recipeReferences) {
        return recipeList;
      }

      listItem.value.recipeReferences.forEach((ref) => {
        const recipe = props.recipes?.get(ref.recipeId);
        if (recipe) {
          recipeList.push(recipe);
        }
      });

      return recipeList;
    });

    return {
      updatedLabels,
      save,
      contextHandler,
      displayRecipeRefs,
      edit,
      contextMenu,
      itemLabelCols,
      listItem,
      localListItem,
      label,
      recipeList,
      toggleEdit,
      isOffline,
    };
  },
});
</script>

<style lang="css">
.strike-through {
  text-decoration: line-through !important;
}
</style>
