<template>
  <v-container v-if="shoppingList" class="md-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/shopping-cart.svg')"></v-img>
      </template>
      <template #title> {{ shoppingList.name }} </template>
    </BasePageTitle>
    <BannerExperimental issue="https://github.com/hay-kot/mealie/issues/916" />
    <!-- Viewer -->
    <section v-if="!edit" class="py-2">
      <div v-if="!byLabel">
        <draggable :value="shoppingList.listItems" handle=".handle" @input="updateIndex">
          <v-lazy v-for="(item, index) in listItems.unchecked" :key="item.id">
            <ShoppingListItem
              v-model="listItems.unchecked[index]"
              :labels="allLabels"
              @checked="saveListItem(item)"
              @save="saveListItem(item)"
              @delete="deleteListItem(item)"
            />
          </v-lazy>
        </draggable>
      </div>

      <!-- View By Label -->
      <div v-else>
        <div v-for="(value, key) in itemsByLabel" :key="key" class="mb-6">
          <div @click="toggleShowChecked()">
            <span>
              <v-icon>
                {{ $globals.icons.tags }}
              </v-icon>
            </span>
            {{ key }}
          </div>
          <v-lazy v-for="(item, index) in value" :key="item.id">
            <ShoppingListItem
              v-model="value[index]"
              :labels="allLabels"
              @checked="saveListItem(item)"
              @save="saveListItem(item)"
              @delete="deleteListItem(item)"
            />
          </v-lazy>
        </div>
      </div>

      <!-- Create Item -->
      <div v-if="createEditorOpen">
        <ShoppingListItemEditor
          v-model="createListItemData"
          class="my-4"
          :labels="allLabels"
          @delete="createEditorOpen = false"
          @cancel="createEditorOpen = false"
          @save="createListItem"
        />
      </div>
      <div v-else class="mt-4 d-flex justify-end">
        <BaseButton create @click="createEditorOpen = true" />
      </div>

      <!-- Checked Items -->
      <div v-if="listItems.checked && listItems.checked.length > 0" class="mt-6">
        <button @click="toggleShowChecked()">
          <span>
            <v-icon>
              {{ showChecked ? $globals.icons.chevronDown : $globals.icons.chevronRight }}
            </v-icon>
          </span>
          {{ listItems.checked ? listItems.checked.length : 0 }} items checked
        </button>
        <v-divider class="my-4"></v-divider>
        <v-expand-transition>
          <div v-show="showChecked">
            <div v-for="(item, idx) in listItems.checked" :key="item.id">
              <ShoppingListItem
                v-model="listItems.checked[idx]"
                class="strike-through-note"
                :labels="allLabels"
                @checked="saveListItem(item)"
                @save="saveListItem(item)"
                @delete="deleteListItem(item)"
              />
            </div>
          </div>
        </v-expand-transition>
      </div>
    </section>

    <!-- Action Bar -->
    <div class="d-flex justify-end mb-4">
      <BaseButtonGroup
        v-if="!edit"
        :buttons="[
          {
            icon: $globals.icons.contentCopy,
            text: '',
            event: 'edit',
            children: [
              {
                icon: $globals.icons.contentCopy,
                text: 'Copy as Text',
                event: 'copy-plain',
              },
              {
                icon: $globals.icons.contentCopy,
                text: 'Copy as Markdown',
                event: 'copy-markdown',
              },
            ],
          },
          {
            icon: $globals.icons.delete,
            text: 'Delete Checked',
            event: 'delete',
          },
          {
            icon: $globals.icons.tags,
            text: 'Toggle Label Sort',
            event: 'sort-by-labels',
          },
          {
            icon: $globals.icons.checkboxBlankOutline,
            text: 'Uncheck All Items',
            event: 'uncheck',
          },
          {
            icon: $globals.icons.primary,
            text: 'Add Recipe',
            event: 'recipe',
          },
        ]"
        @edit="edit = true"
        @delete="deleteChecked"
        @uncheck="uncheckAll"
        @sort-by-labels="sortByLabels"
        @copy-plain="copyListItems('plain')"
        @copy-markdown="copyListItems('markdown')"
      />
      <BaseButton v-else save @click="saveList" />
    </div>

    <!-- Recipe References -->
    <v-lazy>
      <section>
        <div>
          <span>
            <v-icon left class="mb-1">
              {{ $globals.icons.primary }}
            </v-icon>
          </span>
          {{ shoppingList.recipeReferences ? shoppingList.recipeReferences.length : 0 }} Linked Recipes
        </div>
        <v-divider class="my-4"></v-divider>
        <RecipeList :recipes="listRecipes">
          <template v-for="(recipe, index) in listRecipes" #[`actions-${recipe.id}`]>
            <v-list-item-action :key="'item-actions-decrease' + recipe.id">
              <v-btn icon @click.prevent="removeRecipeReferenceToList(recipe.id)">
                <v-icon color="grey lighten-1">{{ $globals.icons.minus }}</v-icon>
              </v-btn>
            </v-list-item-action>
            <div :key="'item-actions-quantity' + recipe.id" class="pl-3">
              {{ shoppingList.recipeReferences[index].recipeQuantity }}
            </div>
            <v-list-item-action :key="'item-actions-increase' + recipe.id">
              <v-btn icon @click.prevent="addRecipeReferenceToList(recipe.id)">
                <v-icon color="grey lighten-1">{{ $globals.icons.createAlt }}</v-icon>
              </v-btn>
            </v-list-item-action>
          </template>
        </RecipeList>
      </section>
    </v-lazy>

    <v-lazy>
      <div class="d-flex justify-end mt-10">
        <ButtonLink to="/shopping-lists/labels" text="Manage Labels" :icon="$globals.icons.tags" />
      </div>
    </v-lazy>
  </v-container>
</template>

<script lang="ts">
import draggable from "vuedraggable";

import { defineComponent, useAsync, useRoute, computed, ref } from "@nuxtjs/composition-api";
import { useClipboard, useToggle } from "@vueuse/core";
import { useUserApi } from "~/composables/api";
import { useAsyncKey } from "~/composables/use-utils";
import { alert } from "~/composables/use-toast";
import ShoppingListItem from "~/components/Domain/ShoppingList/ShoppingListItem.vue";
import BannerExperimental from "~/components/global/BannerExperimental.vue";
import { MultiPurposeLabelOut } from "~/types/api-types/labels";
import { ShoppingListItemCreate, ShoppingListItemOut } from "~/types/api-types/group";
import RecipeList from "~/components/Domain/Recipe/RecipeList.vue";
import ShoppingListItemEditor from "~/components/Domain/ShoppingList/ShoppingListItemEditor.vue";
type CopyTypes = "plain" | "markdown";

interface PresentLabel {
  id: string;
  name: string;
}

export default defineComponent({
  components: {
    draggable,
    ShoppingListItem,
    BannerExperimental,
    RecipeList,
    ShoppingListItemEditor,
  },
  setup() {
    const userApi = useUserApi();

    const edit = ref(false);
    const byLabel = ref(false);

    const route = useRoute();
    const id = route.value.params.id;

    // ===============================================================
    // Shopping List Actions

    const shoppingList = useAsync(async () => {
      return await fetchShoppingList();
    }, useAsyncKey());

    async function fetchShoppingList() {
      const { data } = await userApi.shopping.lists.getOne(id);
      return data;
    }

    async function refresh() {
      shoppingList.value = await fetchShoppingList();
    }

    // =====================================
    // List Item CRUD

    const listItems = computed(() => {
      return {
        checked: shoppingList.value?.listItems?.filter((item) => item.checked) ?? [],
        unchecked: shoppingList.value?.listItems?.filter((item) => !item.checked) ?? [],
      };
    });

    const [showChecked, toggleShowChecked] = useToggle(false);

    // =====================================
    // Copy List Items

    const { copy, copied, isSupported } = useClipboard();

    function getItemsAsPlain(items: ShoppingListItemCreate[]) {
      return items
        .map((item) => {
          return `${item.quantity || ""} x ${item.unit?.name || ""} ${item.food?.name || ""} ${
            item.note || ""
          }`.replace(/\s+/g, " ");
        })
        .join("\n");
    }

    function getItemsAsMarkdown(items: ShoppingListItemCreate[]) {
      return items
        .map((item) => {
          return `- [ ] ${item.quantity || ""} x ${item.unit?.name || ""} ${item.food?.name || ""} ${
            item.note || ""
          }`.replace(/\s+/g, " ");
        })
        .join("\n");
    }

    async function copyListItems(copyType: CopyTypes) {
      if (!isSupported) {
        alert.error("Copy to clipboard is not supported in your browser or environment.");
      }

      console.log("copyListItems", copyType);
      const items = shoppingList.value?.listItems?.filter((item) => !item.checked);

      if (!items) {
        return;
      }

      let text = "";

      switch (copyType) {
        case "markdown":
          text = getItemsAsMarkdown(items);
          break;
        default:
          text = getItemsAsPlain(items);
          break;
      }

      await copy(text);

      if (copied) {
        alert.success(`Copied ${items.length} items to clipboard`);
      }
    }

    // =====================================
    // Check / Uncheck All

    function uncheckAll() {
      let hasChanged = false;
      shoppingList.value?.listItems?.forEach((item) => {
        if (item.checked) {
          hasChanged = true;
          item.checked = false;
        }
      });
      if (hasChanged) {
        saveList();
      }
    }

    function deleteChecked() {
      const unchecked = shoppingList.value?.listItems?.filter((item) => !item.checked);

      if (unchecked?.length === shoppingList.value?.listItems?.length) {
        return;
      }

      if (shoppingList.value?.listItems) {
        shoppingList.value.listItems = unchecked || [];
      }

      saveList();
    }

    // =====================================
    // List Item Context Menu

    const contextActions = {
      delete: "delete",
      setIngredient: "setIngredient",
    };

    const contextMenu = [
      { title: "Delete", action: contextActions.delete },
      { title: "Ingredient", action: contextActions.setIngredient },
    ];

    function contextMenuAction(action: string, item: ShoppingListItemOut, idx: number) {
      if (!shoppingList.value?.listItems) {
        return;
      }

      switch (action) {
        case contextActions.delete:
          shoppingList.value.listItems = shoppingList.value?.listItems.filter((itm) => itm.id !== item.id);
          break;
        case contextActions.setIngredient:
          shoppingList.value.listItems[idx].isFood = !shoppingList.value.listItems[idx].isFood;
          break;
        default:
          break;
      }
    }

    // =====================================
    // Labels
    // TODO: Extract to Composable

    const allLabels = ref([] as MultiPurposeLabelOut[]);

    function sortByLabels() {
      byLabel.value = !byLabel.value;
    }

    const presentLabels = computed(() => {
      const labels: PresentLabel[] = [];

      shoppingList.value?.listItems?.forEach((item) => {
        if (item.labelId && item.label) {
          labels.push({
            name: item.label.name,
            id: item.labelId,
          });
        }
      });

      return labels;
    });

    const itemsByLabel = computed(() => {
      const items: { [prop: string]: ShoppingListItemCreate[] } = {};

      const noLabel = {
        "No Label": [],
      };

      shoppingList.value?.listItems?.forEach((item) => {
        if (item.checked) {
          return;
        }

        if (item.labelId) {
          if (item.label && item.label.name in items) {
            items[item.label.name].push(item);
          } else if (item.label) {
            items[item.label.name] = [item];
          }
        } else {
          // @ts-ignore
          noLabel["No Label"].push(item);
        }
      });

      if (noLabel["No Label"].length > 0) {
        items["No Label"] = noLabel["No Label"];
      }

      return items;
    });

    async function refreshLabels() {
      const { data } = await userApi.multiPurposeLabels.getAll();
      allLabels.value = data ?? [];
    }

    refreshLabels();

    // =====================================
    // Add/Remove Recipe References

    const listRecipes = computed<Array<any>>(() => {
      // @ts-ignore // TODO: Error with Type Generation for recipeReference - eslint bug as well
      return shoppingList.value?.recipeReferences?.map((ref) => ref.recipe) ?? []; // eslint-disable-line
    });

    async function addRecipeReferenceToList(recipeId: number) {
      if (!shoppingList.value) {
        return;
      }

      const { data } = await userApi.shopping.lists.addRecipe(shoppingList.value.id, recipeId);
      console.log(data);

      if (data) {
        refresh();
      }
    }

    async function removeRecipeReferenceToList(recipeId: number) {
      if (!shoppingList.value) {
        return;
      }

      const { data } = await userApi.shopping.lists.removeRecipe(shoppingList.value.id, recipeId);
      console.log(data);

      if (data) {
        refresh();
      }
    }

    // =====================================
    // List Item CRUD

    async function saveListItem(item: ShoppingListItemOut) {
      if (!shoppingList.value) {
        return;
      }

      const { data } = await userApi.shopping.items.updateOne(item.id, item);

      if (data) {
        refresh();
      }
    }

    async function deleteListItem(item: ShoppingListItemOut) {
      if (!shoppingList.value) {
        return;
      }

      const { data } = await userApi.shopping.items.deleteOne(item.id);

      if (data) {
        refresh();
      }
    }

    async function saveList() {
      if (!shoppingList.value?.listItems) {
        return;
      }

      // Set Position
      shoppingList.value.listItems = shoppingList.value.listItems.map((itm: ShoppingListItemOut, idx: number) => {
        itm.position = idx;
        return itm;
      });

      await userApi.shopping.lists.updateOne(id, shoppingList.value);
      refresh();
      edit.value = false;
    }

    function updateIndex(data: ShoppingListItemOut[]) {
      if (shoppingList.value?.listItems) {
        shoppingList.value.listItems = data;
      }

      if (!edit.value) {
        saveList();
      }
    }

    // =====================================
    // Create New Item

    const createEditorOpen = ref(false);
    const createListItemData = ref<ShoppingListItemCreate>(ingredientResetFactory());

    function ingredientResetFactory(): ShoppingListItemCreate {
      return {
        shoppingListId: id,
        checked: false,
        position: shoppingList.value?.listItems?.length || 1,
        isFood: false,
        quantity: 1,
        note: "",
        unit: undefined,
        food: undefined,
        labelId: undefined,
      };
    }

    async function createListItem() {
      if (!shoppingList.value) {
        return;
      }

      const { data } = await userApi.shopping.items.createOne(createListItemData.value);

      if (data) {
        createListItemData.value = ingredientResetFactory();
        createEditorOpen.value = false;
        refresh();
      }
    }

    return {
      addRecipeReferenceToList,
      allLabels,
      byLabel,
      contextMenu,
      contextMenuAction,
      copyListItems,
      createEditorOpen,
      createListItem,
      createListItemData,
      deleteChecked,
      deleteListItem,
      edit,
      itemsByLabel,
      listItems,
      listRecipes,
      presentLabels,
      removeRecipeReferenceToList,
      saveList,
      saveListItem,
      shoppingList,
      showChecked,
      sortByLabels,
      toggleShowChecked,
      uncheckAll,
      updateIndex,
    };
  },
  head() {
    return {
      title: this.$t("shopping-list.shopping-list") as string,
    };
  },
});
</script>

<style scoped>
.number-input-container {
  max-width: 50px;
}
</style>
