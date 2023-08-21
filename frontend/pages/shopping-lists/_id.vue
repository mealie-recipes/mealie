<template>
  <v-container v-if="shoppingList" class="md-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/shopping-cart.svg')"></v-img>
      </template>
      <template #title> {{ shoppingList.name }} </template>
    </BasePageTitle>

    <!-- Viewer -->
    <section v-if="!edit" class="py-2">
      <div v-if="!preferences.viewByLabel">
        <draggable :value="listItems.unchecked" handle=".handle" delay="250" :delay-on-touch-only="true"  @start="loadingCounter += 1" @end="loadingCounter -= 1" @input="updateIndexUnchecked">
          <v-lazy v-for="(item, index) in listItems.unchecked" :key="item.id" class="my-2">
            <ShoppingListItem
              v-model="listItems.unchecked[index]"
              class="my-2 my-sm-0"
              :show-label=true
              :labels="allLabels || []"
              :units="allUnits || []"
              :foods="allFoods || []"
              :recipes="recipeMap"
              @checked="saveListItem"
              @save="saveListItem"
              @delete="deleteListItem(item)"
            />
          </v-lazy>
        </draggable>
      </div>

      <!-- View By Label -->
      <div v-else>
        <div v-for="(value, key, idx) in itemsByLabel" :key="key" class="mb-6">
          <div @click="toggleShowChecked()">
            <span v-if="idx || key !== $tc('shopping-list.no-label')">
              <v-icon :color="getLabelColor(value[0])">
                {{ $globals.icons.tags }}
              </v-icon>
            </span>
            {{ key }}
          </div>
          <draggable :value="value" handle=".handle" delay="250" :delay-on-touch-only="true" @start="loadingCounter += 1" @end="loadingCounter -= 1" @input="updateIndexUncheckedByLabel(key, $event)">
            <v-lazy v-for="(item, index) in value" :key="item.id" class="ml-2 my-2">
              <ShoppingListItem
                v-model="value[index]"
                :show-label=false
                :labels="allLabels || []"
                :units="allUnits || []"
                :foods="allFoods || []"
                :recipes="recipeMap"
                @checked="saveListItem"
                @save="saveListItem"
                @delete="deleteListItem(item)"
              />
            </v-lazy>
          </draggable>
        </div>
      </div>

      <!-- Reorder Labels -->
      <BaseDialog v-model="reorderLabelsDialog" :icon="$globals.icons.tagArrowUp" :title="$t('shopping-list.reorder-labels')">
        <v-card height="fit-content" max-height="70vh" style="overflow-y: auto;">
          <draggable :value="shoppingList.labelSettings" handle=".handle" class="my-2" @start="loadingCounter += 1" @end="loadingCounter -= 1" @input="updateLabelOrder">
            <div v-for="(labelSetting, index) in shoppingList.labelSettings" :key="labelSetting.id">
              <MultiPurposeLabelSection v-model="shoppingList.labelSettings[index]" use-color />
            </div>
          </draggable>
        </v-card>
      </BaseDialog>

      <!-- Create Item -->
      <div v-if="createEditorOpen">
        <ShoppingListItemEditor
          v-model="createListItemData"
          class="my-4"
          :labels="allLabels || []"
          :units="allUnits || []"
          :foods="allFoods || []"
          @delete="createEditorOpen = false"
          @cancel="createEditorOpen = false"
          @save="createListItem"
        />
      </div>
      <div v-else class="mt-4 d-flex justify-end">
        <BaseButton v-if="preferences.viewByLabel" color="info" class="mr-2" @click="reorderLabelsDialog = true">
          <template #icon> {{ $globals.icons.tags }} </template>
          {{ $t('shopping-list.reorder-labels') }}
        </BaseButton>
        <BaseButton create @click="createEditorOpen = true" />
      </div>

      <!-- Action Bar -->
      <div class="d-flex justify-end mb-4 mt-2">
        <BaseButtonGroup
          :buttons="[
            {
              icon: $globals.icons.contentCopy,
              text: '',
              event: 'edit',
              children: [
                {
                  icon: $globals.icons.contentCopy,
                  text: $tc('shopping-list.copy-as-text'),
                  event: 'copy-plain',
                },
                {
                  icon: $globals.icons.contentCopy,
                  text: $tc('shopping-list.copy-as-markdown'),
                  event: 'copy-markdown',
                },
              ],
            },
            {
              icon: $globals.icons.delete,
              text: $tc('shopping-list.delete-checked'),
              event: 'delete',
            },
            {
              icon: $globals.icons.tags,
              text: $tc('shopping-list.toggle-label-sort'),
              event: 'sort-by-labels',
            },
            {
              icon: $globals.icons.checkboxBlankOutline,
              text: $tc('shopping-list.uncheck-all-items'),
              event: 'uncheck',
            },
          ]"
          @edit="edit = true"
          @delete="deleteChecked"
          @uncheck="uncheckAll"
          @sort-by-labels="sortByLabels"
          @copy-plain="copyListItems('plain')"
          @copy-markdown="copyListItems('markdown')"
        />
      </div>

      <!-- Checked Items -->
      <div v-if="listItems.checked && listItems.checked.length > 0" class="mt-6">
        <button @click="toggleShowChecked()">
          <span>
            <v-icon>
              {{ showChecked ? $globals.icons.chevronDown : $globals.icons.chevronRight }}
            </v-icon>
          </span>
          {{ $tc('shopping-list.items-checked-count', listItems.checked ? listItems.checked.length : 0) }}
        </button>
        <v-divider class="my-4"></v-divider>
        <v-expand-transition>
          <div v-show="showChecked">
            <div v-for="(item, idx) in listItems.checked" :key="item.id">
              <ShoppingListItem
                v-model="listItems.checked[idx]"
                class="strike-through-note"
                :labels="allLabels || []"
                :units="allUnits || []"
                :foods="allFoods || []"
                @checked="saveListItem"
                @save="saveListItem"
                @delete="deleteListItem(item)"
              />
            </div>
          </div>
        </v-expand-transition>
      </div>
    </section>

    <!-- Recipe References -->
    <v-lazy v-if="shoppingList.recipeReferences && shoppingList.recipeReferences.length > 0">
      <section>
        <div>
          <span>
            <v-icon left class="mb-1">
              {{ $globals.icons.primary }}
            </v-icon>
          </span>
          {{ $tc('shopping-list.linked-recipes-count', shoppingList.recipeReferences ? shoppingList.recipeReferences.length : 0) }}
        </div>
        <v-divider class="my-4"></v-divider>
        <RecipeList :recipes="Array.from(recipeMap.values())" show-description>
          <template v-for="(recipe, index) in recipeMap.values()" #[`actions-${recipe.id}`]>
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
        <ButtonLink to="/group/data/labels" :text="$tc('shopping-list.manage-labels')" :icon="$globals.icons.tags" />
      </div>
    </v-lazy>
  </v-container>
</template>

<script lang="ts">
import draggable from "vuedraggable";

import { defineComponent, useRoute, computed, ref, onUnmounted, useContext } from "@nuxtjs/composition-api";
import { useIdle, useToggle } from "@vueuse/core";
import { useCopyList } from "~/composables/use-copy";
import { useUserApi } from "~/composables/api";
import MultiPurposeLabelSection from "~/components/Domain/ShoppingList/MultiPurposeLabelSection.vue"
import ShoppingListItem from "~/components/Domain/ShoppingList/ShoppingListItem.vue";
import { ShoppingListItemCreate, ShoppingListItemOut, ShoppingListMultiPurposeLabelOut, ShoppingListOut } from "~/lib/api/types/group";
import RecipeList from "~/components/Domain/Recipe/RecipeList.vue";
import ShoppingListItemEditor from "~/components/Domain/ShoppingList/ShoppingListItemEditor.vue";
import { useFoodStore, useLabelStore, useUnitStore } from "~/composables/store";
import { useShoppingListPreferences } from "~/composables/use-users/preferences";

type CopyTypes = "plain" | "markdown";

interface PresentLabel {
  id: string;
  name: string;
}

export default defineComponent({
  components: {
    draggable,
    MultiPurposeLabelSection,
    ShoppingListItem,
    RecipeList,
    ShoppingListItemEditor,
  },
  setup() {
    const preferences = useShoppingListPreferences();

    const { idle } = useIdle(5 * 60 * 1000) // 5 minutes
    const loadingCounter = ref(1);
    const recipeReferenceLoading = ref(false);
    const userApi = useUserApi();

    const edit = ref(false);
    const reorderLabelsDialog = ref(false);

    const route = useRoute();
    const id = route.value.params.id;

    const { i18n } = useContext();

    // ===============================================================
    // Shopping List Actions

    const shoppingList = ref<ShoppingListOut | null>(null);
    async function fetchShoppingList() {
      const { data } = await userApi.shopping.lists.getOne(id);
      return data;
    }

    async function refresh() {
      loadingCounter.value += 1;
      const newListValue = await fetchShoppingList();
      loadingCounter.value -= 1;

      // only update the list with the new value if we're not loading, to prevent UI jitter
      if (!loadingCounter.value) {
        shoppingList.value = newListValue;
        updateItemsByLabel();
      }
    }

    // constantly polls for changes
    async function pollForChanges() {
      // pause polling if the user isn't active or we're busy
      if (idle.value || loadingCounter.value) {
        return;
      }

      try {
        await refresh();

        if (shoppingList.value) {
          attempts = 0;
          return;
        }

        // if the refresh was unsuccessful, the shopping list will be null, so we increment the attempt counter
        attempts ++;
      }

      catch (error) {
        attempts ++;
      }

      // if we hit too many errors, stop polling
      if (attempts >= maxAttempts) {
        clearInterval(pollTimer);
      }
    }

    // start polling
    loadingCounter.value -= 1;
    const pollFrequency = 5000;
    pollForChanges();  // populate initial list

    let attempts = 0;
    const maxAttempts = 3;

    const pollTimer: ReturnType<typeof setInterval> = setInterval(() => { pollForChanges() }, pollFrequency);
    onUnmounted(() => {
      clearInterval(pollTimer);
    });

    // =====================================
    // List Item CRUD

    const listItems = computed(() => {
      return {
        unchecked: shoppingList.value?.listItems?.filter((item) => !item.checked) ?? [],
        checked: shoppingList.value?.listItems
          ?.filter((item) => item.checked)
          .sort((a, b) => (a.updateAt < b.updateAt ? 1 : -1))
          ?? [],
      };
    });

    const [showChecked, toggleShowChecked] = useToggle(false);

    // =====================================
    // Copy List Items

    const copy = useCopyList();

    function copyListItems(copyType: CopyTypes) {
      const items = shoppingList.value?.listItems?.filter((item) => !item.checked);

      if (!items) {
        return;
      }

      const text: string[] = items.map((itm) => itm.display || "");

      switch (copyType) {
        case "markdown":
          copy.copyMarkdownCheckList(text);
          break;
        default:
          copy.copyPlain(text);
          break;
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
        updateListItems();
      }
    }

    function deleteChecked() {
      const checked = shoppingList.value?.listItems?.filter((item) => item.checked);

      if (!checked || checked?.length === 0) {
        return;
      }

      loadingCounter.value += 1;
      deleteListItems(checked);

      loadingCounter.value -= 1;
      refresh();
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
    // Labels, Units, Foods
    // TODO: Extract to Composable

    const { labels: allLabels } = useLabelStore();
    const { units: allUnits } = useUnitStore();
    const { foods: allFoods } = useFoodStore();

    function getLabelColor(item: ShoppingListItemOut | null) {
      return item?.label?.color;
    }

    function sortByLabels() {
      preferences.value.viewByLabel = !preferences.value.viewByLabel;
    }

    function toggleReorderLabelsDialog() {
      reorderLabelsDialog.value = !reorderLabelsDialog.value
    }

    async function updateLabelOrder(labelSettings: ShoppingListMultiPurposeLabelOut[]) {
      if (!shoppingList.value) {
        return;
      }

      labelSettings.forEach((labelSetting, index) => {
        labelSetting.position = index;
        return labelSetting;
      });

      // setting this doesn't have any effect on the data since it's refreshed automatically, but it makes the ux feel smoother
      shoppingList.value.labelSettings = labelSettings;
      updateItemsByLabel();

      loadingCounter.value += 1;
      const { data } = await userApi.shopping.lists.updateLabelSettings(shoppingList.value.id, labelSettings);
      loadingCounter.value -= 1;

      if (data) {
        refresh();
      }
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

    const itemsByLabel = ref<{ [key: string]: ShoppingListItemOut[] }>({});

    function updateItemsByLabel() {
      const items: { [prop: string]: ShoppingListItemOut[] } = {};
      const noLabelText = i18n.tc("shopping-list.no-label");
      const noLabel = [] as ShoppingListItemOut[];

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
          noLabel.push(item);
        }
      });

      if (noLabel.length > 0) {
        items[noLabelText] = noLabel;
      }

      // sort the map by label order
      const orderedLabelNames = shoppingList.value?.labelSettings?.map((labelSetting) => { return labelSetting.label.name; })
      if (!orderedLabelNames) {
        itemsByLabel.value = items;
        return;
      }

      const itemsSorted: { [prop: string]: ShoppingListItemOut[] } = {};
      if (noLabelText in items) {
        itemsSorted[noLabelText] = items[noLabelText];
      }

      orderedLabelNames.forEach(labelName => {
        if (labelName in items) {
          itemsSorted[labelName] = items[labelName];
        }
      });

      itemsByLabel.value = itemsSorted;
    }

    async function refreshLabels() {
      const { data } = await userApi.multiPurposeLabels.getAll();

      if (data) {
        allLabels.value = data.items ?? [];
      }
    }

    refreshLabels();

    // =====================================
    // Add/Remove Recipe References

    const recipeMap = computed(() => new Map(
      (shoppingList.value?.recipeReferences?.map((ref) => ref.recipe) ?? [])
        .map((recipe) => [recipe.id || "", recipe]))
    );

    async function addRecipeReferenceToList(recipeId: string) {
      if (!shoppingList.value || recipeReferenceLoading.value) {
        return;
      }

      loadingCounter.value += 1;
      recipeReferenceLoading.value = true;
      const { data } = await userApi.shopping.lists.addRecipe(shoppingList.value.id, recipeId);
      recipeReferenceLoading.value = false;
      loadingCounter.value -= 1;

      if (data) {
        refresh();
      }
    }

    async function removeRecipeReferenceToList(recipeId: string) {
      if (!shoppingList.value || recipeReferenceLoading.value) {
        return;
      }

      loadingCounter.value += 1;
      recipeReferenceLoading.value = true;
      const { data } = await userApi.shopping.lists.removeRecipe(shoppingList.value.id, recipeId);
      recipeReferenceLoading.value = false;
      loadingCounter.value -= 1;

      if (data) {
        refresh();
      }
    }

    // =====================================
    // List Item CRUD

    /*
     * saveListItem updates and update on the backend server. Additionally, if the item is
     * checked it will also append that item to the end of the list so that the unchecked items
     * are at the top of the list.
     */
    async function saveListItem(item: ShoppingListItemOut) {
      if (!shoppingList.value) {
        return;
      }

      if (item.checked && shoppingList.value.listItems) {
        const lst = shoppingList.value.listItems.filter((itm) => itm.id !== item.id);
        lst.push(item);

        // make sure the item is at the end of the list with the other checked items
        item.position = shoppingList.value.listItems.length;

        // set a temporary updatedAt timestamp prior to refresh so it appears at the top of the checked items
        item.updateAt = new Date().toISOString();
        item.updateAt = item.updateAt.substring(0, item.updateAt.length-1);
      }

      // make updates reflect immediately
      if (shoppingList.value.listItems) {
        shoppingList.value.listItems.forEach((oldListItem: ShoppingListItemOut, idx: number) => {
          if (oldListItem.id === item.id && shoppingList.value?.listItems) {
            shoppingList.value.listItems[idx] = item;
          }
        });
      }

      updateItemsByLabel();

      loadingCounter.value += 1;
      const { data } = await userApi.shopping.items.updateOne(item.id, item);
      loadingCounter.value -= 1;

      if (data) {
        refresh();
      }
    }

    async function deleteListItem(item: ShoppingListItemOut) {
      if (!shoppingList.value) {
        return;
      }

      loadingCounter.value += 1;
      const { data } = await userApi.shopping.items.deleteOne(item.id);
      loadingCounter.value -= 1;

      if (data) {
        refresh();
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
        labelId: undefined,
        unitId: undefined,
        foodId: undefined,
      };
    }

    async function createListItem() {
      if (!shoppingList.value) {
        return;
      }

      loadingCounter.value += 1;

      // make sure it's inserted into the end of the list, which may have been updated
      createListItemData.value.position = shoppingList.value?.listItems?.length || 1;
      const { data } = await userApi.shopping.items.createOne(createListItemData.value);
      loadingCounter.value -= 1;

      if (data) {
        createListItemData.value = ingredientResetFactory();
        createEditorOpen.value = false;
        refresh();
      }
    }

    function updateIndexUnchecked(uncheckedItems: ShoppingListItemOut[]) {
      if (shoppingList.value?.listItems) {
        // move the new unchecked items in front of the checked items
        shoppingList.value.listItems = uncheckedItems.concat(listItems.value.checked);
      }

      updateListItems();
    }

    function updateIndexUncheckedByLabel(labelName: string, labeledUncheckedItems: ShoppingListItemOut[]) {
      if (!itemsByLabel.value[labelName]) {
        return;
      }

      // update this label's item order
      itemsByLabel.value[labelName] = labeledUncheckedItems;

      // reset list order of all items
      const allUncheckedItems: ShoppingListItemOut[] = [];
      for (labelName in itemsByLabel.value) {
        allUncheckedItems.push(...itemsByLabel.value[labelName]);
      }

      // save changes
      return updateIndexUnchecked(allUncheckedItems);
    }

    async function deleteListItems(items: ShoppingListItemOut[]) {
      if (!shoppingList.value) {
        return;
      }

      loadingCounter.value += 1;
      const { data } = await userApi.shopping.items.deleteMany(items);
      loadingCounter.value -= 1;

      if (data) {
        refresh();
      }
    }

    async function updateListItems() {
      if (!shoppingList.value?.listItems) {
        return;
      }

      // Set Position
      shoppingList.value.listItems = listItems.value.unchecked.concat(listItems.value.checked).map((itm: ShoppingListItemOut, idx: number) => {
        itm.position = idx;
        return itm;
      });

      loadingCounter.value += 1;
      const { data } = await userApi.shopping.items.updateMany(shoppingList.value.listItems);
      loadingCounter.value -= 1;

      if (data) {
        refresh();
      }
    }

    return {
      addRecipeReferenceToList,
      updateListItems,
      allLabels,
      contextMenu,
      contextMenuAction,
      copyListItems,
      createEditorOpen,
      createListItem,
      createListItemData,
      deleteChecked,
      deleteListItem,
      edit,
      getLabelColor,
      itemsByLabel,
      listItems,
      loadingCounter,
      preferences,
      presentLabels,
      recipeMap,
      removeRecipeReferenceToList,
      reorderLabelsDialog,
      toggleReorderLabelsDialog,
      updateLabelOrder,
      saveListItem,
      shoppingList,
      showChecked,
      sortByLabels,
      toggleShowChecked,
      uncheckAll,
      updateIndexUnchecked,
      updateIndexUncheckedByLabel,
      allUnits,
      allFoods,
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
