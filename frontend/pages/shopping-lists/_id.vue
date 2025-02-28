<template>
  <v-container v-if="shoppingList" class="md-container">
    <BaseDialog v-model="checkAllDialog" :title="$tc('general.confirm')" @confirm="checkAll">
      <v-card-text>{{ $t('shopping-list.are-you-sure-you-want-to-check-all-items') }}</v-card-text>
    </BaseDialog>

    <BaseDialog v-model="uncheckAllDialog" :title="$tc('general.confirm')" @confirm="uncheckAll">
      <v-card-text>{{ $t('shopping-list.are-you-sure-you-want-to-uncheck-all-items') }}</v-card-text>
    </BaseDialog>

    <BaseDialog v-model="deleteCheckedDialog" :title="$tc('general.confirm')" @confirm="deleteChecked">
      <v-card-text>{{ $t('shopping-list.are-you-sure-you-want-to-delete-checked-items') }}</v-card-text>
    </BaseDialog>

    <BasePageTitle divider>
      <template #header>
        <v-container>
          <v-row>
            <v-col cols="3" class="text-left">
              <ButtonLink :to="`/shopping-lists?disableRedirect=true`" :text="$tc('shopping-list.all-lists')" :icon="$globals.icons.backArrow" />
            </v-col>
            <v-col cols="6" class="d-none d-lg-flex justify-center">
              <v-img max-height="100" max-width="100" :src="require('~/static/svgs/shopping-cart.svg')"></v-img>
            </v-col>
            <v-col class="d-flex justify-end">
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
                    icon: $globals.icons.checkboxOutline,
                    text: $tc('shopping-list.check-all-items'),
                    event: 'check',
                  },
                  {
                    icon: $globals.icons.dotsVertical,
                    text: '',
                    event: 'three-dot',
                    children: [
                      {
                        icon: $globals.icons.tags,
                        text: $tc('shopping-list.toggle-label-sort'),
                        event: 'sort-by-labels',
                      },
                      {
                        icon: $globals.icons.tags,
                        text: $tc('shopping-list.reorder-labels'),
                        event: 'reorder-labels',
                      },
                      {
                        icon: $globals.icons.tags,
                        text: $tc('shopping-list.manage-labels'),
                        event: 'manage-labels',
                      },
                    ],
                  },
                ]"
                @edit="edit = true"
                @three-dot="threeDot = true"
                @check="openCheckAll"
                @sort-by-labels="sortByLabels"
                @copy-plain="copyListItems('plain')"
                @copy-markdown="copyListItems('markdown')"
                @reorder-labels="toggleReorderLabelsDialog()"
                @manage-labels="$router.push(`/group/data/labels`)"
              />
            </v-col>
          </v-row>
        </v-container>
      </template>
      <template #title> {{ shoppingList.name }} </template>
    </BasePageTitle>
    <BannerWarning
      v-if="$nuxt.isOffline"
      :title="$tc('shopping-list.you-are-offline')"
      :description="$tc('shopping-list.you-are-offline-description')"
    />

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
        <div v-for="(value, key) in itemsByLabel" :key="key" class="pb-4">
          <v-btn
            :color="getLabelColor(value[0]) ? getLabelColor(value[0]) : '#959595'"
            :style="{
                'color': getTextColor(getLabelColor(value[0])),
                'letter-spacing': 'normal',
              }"
            @click="toggleShowLabel(key)"
          >
            <v-icon>
              {{ labelOpenState[key] ? $globals.icons.chevronDown : $globals.icons.chevronRight }}
            </v-icon>
            {{ key }}
          </v-btn>
        <v-divider/>
        <v-expand-transition group>
          <div v-show="labelOpenState[key]">
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
        </v-expand-transition>
        </div>
      </div>

      <!-- Create Item -->
      <div v-if="createEditorOpen">
        <ShoppingListItemEditor
          v-model="createListItemData"
          class="my-4"
          :labels="allLabels || []"
          :units="allUnits || []"
          :foods="allFoods || []"
          :allow-delete="false"
          @delete="createEditorOpen = false"
          @cancel="createEditorOpen = false"
          @save="createListItem"
        />
      </div>
      <div v-else class="d-flex justify-end">
        <BaseButton create @click="createEditorOpen = true" > {{ $t('general.add') }} </BaseButton>
      </div>

      <!-- Reorder Labels -->
      <BaseDialog
        v-model="reorderLabelsDialog"
        :icon="$globals.icons.tagArrowUp"
        :title="$t('shopping-list.reorder-labels')"
        :submit-icon="$globals.icons.save"
        :submit-text="$tc('general.save')"
        @submit="saveLabelOrder"
        @close="cancelLabelOrder">
        <v-card height="fit-content" max-height="70vh" style="overflow-y: auto;">
          <draggable
            v-if="localLabels"
            :value="localLabels"
            handle=".handle"
            delay="250"
            :delay-on-touch-only="true"
            class="my-2"
            @input="updateLabelOrder"
          >
            <div v-for="(labelSetting, index) in localLabels" :key="labelSetting.id">
              <MultiPurposeLabelSection v-model="localLabels[index]" use-color />
            </div>
          </draggable>
        </v-card>
      </BaseDialog>

      <!-- Checked Items -->
      <div v-if="listItems.checked && listItems.checked.length > 0" class="mt-6">
        <div class="d-flex">
          <div class="flex-grow-1">
            <button @click="toggleShowChecked()">
              <span>
                <v-icon>
                  {{ showChecked ? $globals.icons.chevronDown : $globals.icons.chevronRight }}
                </v-icon>
              </span>
              {{ $tc('shopping-list.items-checked-count', listItems.checked ? listItems.checked.length : 0) }}
            </button>
          </div>
          <div class="justify-end mt-n2">
            <BaseButtonGroup
                :buttons="[
                  {
                    icon: $globals.icons.checkboxBlankOutline,
                    text: $tc('shopping-list.uncheck-all-items'),
                    event: 'uncheck',
                  },
                  {
                    icon: $globals.icons.delete,
                    text: $tc('shopping-list.delete-checked'),
                    event: 'delete',
                  },
                ]"
                @uncheck="openUncheckAll"
                @delete="openDeleteChecked"
              />
            </div>
        </div>
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
        <RecipeList :recipes="Array.from(recipeMap.values())" show-description :disabled="$nuxt.isOffline">
          <template v-for="(recipe, index) in recipeMap.values()" #[`actions-${recipe.id}`]>
            <v-list-item-action :key="'item-actions-decrease' + recipe.id">
              <v-btn icon :disabled="$nuxt.isOffline" @click.prevent="removeRecipeReferenceToList(recipe.id)">
                <v-icon color="grey lighten-1">{{ $globals.icons.minus }}</v-icon>
              </v-btn>
            </v-list-item-action>
            <div :key="'item-actions-quantity' + recipe.id" class="pl-3">
              {{ shoppingList.recipeReferences[index].recipeQuantity }}
            </div>
            <v-list-item-action :key="'item-actions-increase' + recipe.id">
              <v-btn icon :disabled="$nuxt.isOffline" @click.prevent="addRecipeReferenceToList(recipe.id)">
                <v-icon color="grey lighten-1">{{ $globals.icons.createAlt }}</v-icon>
              </v-btn>
            </v-list-item-action>
          </template>
        </RecipeList>
      </section>
    </v-lazy>
    <WakelockSwitch/>
  </v-container>
</template>

<script lang="ts">
import draggable from "vuedraggable";

import { defineComponent, useRoute, computed, ref, toRefs, onUnmounted, useContext, reactive, watch } from "@nuxtjs/composition-api";
import { useIdle, useToggle } from "@vueuse/core";
import { useCopyList } from "~/composables/use-copy";
import { useUserApi } from "~/composables/api";
import MultiPurposeLabelSection from "~/components/Domain/ShoppingList/MultiPurposeLabelSection.vue"
import ShoppingListItem from "~/components/Domain/ShoppingList/ShoppingListItem.vue";
import { ShoppingListItemOut, ShoppingListMultiPurposeLabelOut, ShoppingListOut } from "~/lib/api/types/household";
import RecipeList from "~/components/Domain/Recipe/RecipeList.vue";
import ShoppingListItemEditor from "~/components/Domain/ShoppingList/ShoppingListItemEditor.vue";
import { useFoodStore, useLabelStore, useUnitStore } from "~/composables/store";
import { useShoppingListItemActions } from "~/composables/use-shopping-list-item-actions";
import { useShoppingListPreferences } from "~/composables/use-users/preferences";
import { getTextColor } from "~/composables/use-text-color";
import { uuid4 } from "~/composables/use-utils";

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
  middleware: "auth",
  setup() {
    const { $auth, i18n } = useContext();
    const preferences = useShoppingListPreferences();

    const { idle } = useIdle(5 * 60 * 1000) // 5 minutes
    const loadingCounter = ref(1);
    const recipeReferenceLoading = ref(false);
    const userApi = useUserApi();

    const edit = ref(false);
    const threeDot = ref(false);
    const reorderLabelsDialog = ref(false);
    const preserveItemOrder = ref(false);

    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");
    const id = route.value.params.id;
    const shoppingListItemActions = useShoppingListItemActions(id);

    const state = reactive({
      checkAllDialog: false,
      uncheckAllDialog: false,
      deleteCheckedDialog: false,
    });

    // ===============================================================
    // Shopping List Actions

    const shoppingList = ref<ShoppingListOut | null>(null);
    async function fetchShoppingList() {
      const data = await shoppingListItemActions.getList();
      return data;
    }

    async function refresh() {
      loadingCounter.value += 1;
      try {
        await shoppingListItemActions.process();
      } catch (error) {
        console.error(error);
      }

      let newListValue = null
      try {
        newListValue = await fetchShoppingList();
      } catch (error) {
        console.error(error);
      }

      loadingCounter.value -= 1;

      // only update the list with the new value if we're not loading, to prevent UI jitter
      if (loadingCounter.value) {
        return;
      }

      // if we're not connected to the network, this will be null, so we don't want to clear the list
      if (newListValue) {
        shoppingList.value = newListValue;
      }

      updateListItemOrder();
    }

    function updateListItemOrder() {
      if (!preserveItemOrder.value) {
        groupAndSortListItemsByFood();
      } else {
        sortListItems();
      }
      updateItemsByLabel();
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
    pollForChanges();  // populate initial list

    // max poll time = pollFrequency * maxAttempts = 24 hours
    // we use a long max poll time since polling stops when the user is idle anyway
    const pollFrequency = 5000;
    const maxAttempts = 17280;
    let attempts = 0;

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
          .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))
          ?? [],
      };
    });

    // =====================================
    // Collapsable Labels
    const labelOpenState = ref<{ [key: string]: boolean }>({});

    const initializeLabelOpenStates = () => {
      if (!shoppingList.value?.listItems) return;

      const existingLabels = new Set(Object.keys(labelOpenState.value));
      let hasChanges = false;

      for (const item of shoppingList.value.listItems) {
        const labelName = item.label?.name || i18n.tc("shopping-list.no-label");
        if (!existingLabels.has(labelName) && !(labelName in labelOpenState.value)) {
          labelOpenState.value[labelName] = true;
          hasChanges = true;
        }
      }

      if (hasChanges) {
        labelOpenState.value = { ...labelOpenState.value };
      }
    };

    const labelNames = computed(() => {
      return new Set(
        shoppingList.value?.listItems
          ?.map(item => item.label?.name || i18n.tc("shopping-list.no-label"))
          .filter(Boolean) ?? []
      );
    });

    watch(labelNames, initializeLabelOpenStates, { immediate: true });

    function toggleShowLabel(key: string) {
      labelOpenState.value[key] = !labelOpenState.value[key];
    }

    const [showChecked, toggleShowChecked] = useToggle(false);

    // =====================================
    // Copy List Items

    const copy = useCopyList();

    function copyListItems(copyType: CopyTypes) {
      const text: string[] = [];

      if (preferences.value.viewByLabel) {
        // if we're sorting by label, we want the copied text in subsections
        Object.entries(itemsByLabel.value).forEach(([label, items], idx) => {
          // for every group except the first, add a blank line
          if (idx) {
            text.push("")
          }

          // add an appropriate heading for the label depending on the copy format
          text.push(formatCopiedLabelHeading(copyType, label))

          // now add the appropriately formatted list items with the given label
          items.forEach((item) => text.push(formatCopiedListItem(copyType, item)))
        })
      } else {
        // labels are toggled off, so just copy in the order they come in
        const items = shoppingList.value?.listItems?.filter((item) => !item.checked)

        items?.forEach((item) => {
          text.push(formatCopiedListItem(copyType, item))
        });
      }

      copy.copyPlain(text);
    }

    function formatCopiedListItem(copyType: CopyTypes, item: ShoppingListItemOut): string {
      const display = item.display || ""
      switch (copyType) {
        case "markdown":
          return `- [ ] ${display}`
        default:
          return display
      }
    }

    function formatCopiedLabelHeading(copyType: CopyTypes, label: string): string {
      switch (copyType) {
        case "markdown":
          return `# ${label}`
        default:
          return `[${label}]`
      }
    }

    // =====================================
    // Check / Uncheck All
    function openCheckAll() {
      if (shoppingList.value?.listItems?.some((item) => !item.checked)) {
        state.checkAllDialog = true;
      }
    }

    function checkAll() {
      state.checkAllDialog = false;
      let hasChanged = false;
      shoppingList.value?.listItems?.forEach((item) => {
        if (!item.checked) {
          hasChanged = true;
          item.checked = true;
        }
      });
      if (hasChanged) {
        updateListItems();
      }
    }

    function openUncheckAll() {
      if (shoppingList.value?.listItems?.some((item) => item.checked)) {
        state.uncheckAllDialog = true;
      }
    }

    function uncheckAll() {
      state.uncheckAllDialog = false;
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

    function openDeleteChecked() {
      if (shoppingList.value?.listItems?.some((item) => item.checked)) {
        state.deleteCheckedDialog = true;
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
      { title: i18n.tc("general.delete"), action: contextActions.delete },
      { title: i18n.tc("recipe.ingredient"), action: contextActions.setIngredient },
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

    const localLabels = ref<ShoppingListMultiPurposeLabelOut[]>()

    const { store: allLabels } = useLabelStore();
    const { store: allUnits } = useUnitStore();
    const { store: allFoods } = useFoodStore();

    function getLabelColor(item: ShoppingListItemOut | null) {
      return item?.label?.color;
    }

    function sortByLabels() {
      preferences.value.viewByLabel = !preferences.value.viewByLabel;
    }

    function toggleReorderLabelsDialog() {
      // stop polling and populate localLabels
      loadingCounter.value += 1
      reorderLabelsDialog.value = !reorderLabelsDialog.value
      localLabels.value = shoppingList.value?.labelSettings
    }

    function updateLabelOrder(labelSettings: ShoppingListMultiPurposeLabelOut[]) {
      if (!shoppingList.value) {
        return;
      }

      labelSettings.forEach((labelSetting, index) => {
        labelSetting.position = index;
        return labelSetting;
      });

      localLabels.value = labelSettings
    }

    function cancelLabelOrder() {
      loadingCounter.value -= 1
      if (!shoppingList.value) {
        return;
      }
      // restore original state
      localLabels.value = shoppingList.value.labelSettings
    }

    async function saveLabelOrder() {
      if (!shoppingList.value || !localLabels.value || (localLabels.value === shoppingList.value.labelSettings)) {
        return;
      }

      loadingCounter.value += 1;
      const { data } = await userApi.shopping.lists.updateLabelSettings(shoppingList.value.id, localLabels.value);
      loadingCounter.value -= 1;

      if (data) {
        // update shoppingList labels using the API response
        shoppingList.value.labelSettings = (data as ShoppingListOut).labelSettings;
        updateItemsByLabel();
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

    interface ListItemGroup {
      position: number;
      createdAt: string;
      items: ShoppingListItemOut[];
    }

    function sortItems(a: ShoppingListItemOut | ListItemGroup, b: ShoppingListItemOut | ListItemGroup) {
      return (
        ((a.position || 0) > (b.position || 0)) ||
        ((a.createdAt || "") < (b.createdAt || ""))
        ? 1 : -1
      );
    }

    function groupAndSortListItemsByFood() {
      if (!shoppingList.value?.listItems?.length) {
        return;
      }

      const checkedItemKey = "__checkedItem"
      const listItemGroupsMap = new Map<string, ListItemGroup>();
      listItemGroupsMap.set(checkedItemKey, {position: Number.MAX_SAFE_INTEGER, createdAt: "", items: []});

      // group items by checked status, food, or note
      shoppingList.value.listItems.forEach((item) => {
        const key = item.checked ? checkedItemKey : item.isFood && item.food?.name
          ? item.food.name
          : item.note || ""

        const group = listItemGroupsMap.get(key);
        if (!group) {
          listItemGroupsMap.set(key, {position: item.position || 0, createdAt: item.createdAt || "", items: [item]});
        } else {
          group.items.push(item);
        }
      });

      const listItemGroups = Array.from(listItemGroupsMap.values());
      listItemGroups.sort(sortItems);

      // sort group items, then aggregate them
      const sortedItems: ShoppingListItemOut[] = [];
      let nextPosition = 0;
      listItemGroups.forEach((listItemGroup) => {
        listItemGroup.items.sort(sortItems);
        listItemGroup.items.forEach((item) => {
          item.position = nextPosition;
          nextPosition += 1;
          sortedItems.push(item);
        })
      });

      shoppingList.value.listItems = sortedItems;
    }

    function sortListItems() {
      if (!shoppingList.value?.listItems?.length) {
        return;
      }

      shoppingList.value.listItems.sort(sortItems)
    }

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
      const { data } = await userApi.shopping.lists.addRecipes(shoppingList.value.id, [{ recipeId }]);
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
    function saveListItem(item: ShoppingListItemOut) {
      if (!shoppingList.value) {
        return;
      }

      if (item.checked && shoppingList.value.listItems) {
        const lst = shoppingList.value.listItems.filter((itm) => itm.id !== item.id);
        lst.push(item);

        // make sure the item is at the end of the list with the other checked items
        item.position = shoppingList.value.listItems.length;

        // set a temporary updatedAt timestamp prior to refresh so it appears at the top of the checked items
        item.updatedAt = new Date().toISOString();
      }

      // make updates reflect immediately
      if (shoppingList.value.listItems) {
        shoppingList.value.listItems.forEach((oldListItem: ShoppingListItemOut, idx: number) => {
          if (oldListItem.id === item.id && shoppingList.value?.listItems) {
            shoppingList.value.listItems[idx] = item;
          }
        });
      }

      updateListItemOrder();
      shoppingListItemActions.updateItem(item);
      refresh();
    }

    function deleteListItem(item: ShoppingListItemOut) {
      if (!shoppingList.value) {
        return;
      }

      shoppingListItemActions.deleteItem(item);

      // remove the item from the list immediately so the user sees the change
      if (shoppingList.value.listItems) {
        shoppingList.value.listItems = shoppingList.value.listItems.filter((itm) => itm.id !== item.id);
      }

      refresh();
    }

    // =====================================
    // Create New Item

    const createEditorOpen = ref(false);
    const createListItemData = ref<ShoppingListItemOut>(listItemFactory());

    function listItemFactory(isFood = false): ShoppingListItemOut {
      return {
        id: uuid4(),
        shoppingListId: id,
        checked: false,
        position: shoppingList.value?.listItems?.length || 1,
        isFood,
        quantity: 0,
        note: "",
        labelId: undefined,
        unitId: undefined,
        foodId: undefined,
      };
    }

    function createListItem() {
      if (!shoppingList.value) {
        return;
      }

      if (!createListItemData.value.foodId && !createListItemData.value.note) {
        // don't create an empty item
        return;
      }

      loadingCounter.value += 1;

      // make sure it's inserted into the end of the list, which may have been updated
      createListItemData.value.position = shoppingList.value?.listItems?.length
        ? (shoppingList.value.listItems.reduce((a, b) => (a.position || 0) > (b.position || 0) ? a : b).position || 0) + 1
        : 0;

      createListItemData.value.createdAt = new Date().toISOString();
      createListItemData.value.updatedAt = createListItemData.value.createdAt;

      updateListItemOrder();

      shoppingListItemActions.createItem(createListItemData.value);
      loadingCounter.value -= 1;

      if (shoppingList.value.listItems) {
          // add the item to the list immediately so the user sees the change
          shoppingList.value.listItems.push(createListItemData.value);
          updateListItemOrder();
        }
      createListItemData.value = listItemFactory(createListItemData.value.isFood || false);
      refresh();
    }

    function updateIndexUnchecked(uncheckedItems: ShoppingListItemOut[]) {
      if (shoppingList.value?.listItems) {
        // move the new unchecked items in front of the checked items
        shoppingList.value.listItems = uncheckedItems.concat(listItems.value.checked);
      }

      // since the user has manually reordered the list, we should preserve this order
      preserveItemOrder.value = true;

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

      // since the user has manually reordered the list, we should preserve this order
      preserveItemOrder.value = true;

      // save changes
      return updateIndexUnchecked(allUncheckedItems);
    }

    function deleteListItems(items: ShoppingListItemOut[]) {
      if (!shoppingList.value) {
        return;
      }

      items.forEach((item) => {
        shoppingListItemActions.deleteItem(item);
      });
      // remove the items from the list immediately so the user sees the change
      if (shoppingList.value?.listItems) {
        const deletedItems = new Set(items.map(item => item.id));
        shoppingList.value.listItems = shoppingList.value.listItems.filter((itm) => !deletedItems.has(itm.id));
      }

      refresh();
    }

    function updateListItems() {
      if (!shoppingList.value?.listItems) {
        return;
      }

      // Set Position
      shoppingList.value.listItems = listItems.value.unchecked.concat(listItems.value.checked).map((itm: ShoppingListItemOut, idx: number) => {
        itm.position = idx;
        return itm;
      });

      shoppingList.value.listItems.forEach((item) => {
        shoppingListItemActions.updateItem(item);
      });
      refresh();
    }

    return {
      ...toRefs(state),
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
      openDeleteChecked,
      deleteListItem,
      edit,
      threeDot,
      getLabelColor,
      groupSlug,
      itemsByLabel,
      listItems,
      loadingCounter,
      preferences,
      presentLabels,
      recipeMap,
      removeRecipeReferenceToList,
      reorderLabelsDialog,
      toggleReorderLabelsDialog,
      localLabels,
      updateLabelOrder,
      cancelLabelOrder,
      saveLabelOrder,
      saveListItem,
      shoppingList,
      showChecked,
      sortByLabels,
      labelOpenState,
      toggleShowLabel,
      toggleShowChecked,
      uncheckAll,
      openUncheckAll,
      checkAll,
      openCheckAll,
      updateIndexUnchecked,
      updateIndexUncheckedByLabel,
      allUnits,
      allFoods,
      getTextColor,
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
