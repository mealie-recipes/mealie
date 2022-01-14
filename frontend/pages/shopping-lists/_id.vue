<template>
  <v-container v-if="shoppingList" class="narrow-container">
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
          <ShoppingListItem
            v-for="(item, index) in listItems.unchecked"
            :key="item.id"
            v-model="listItems.unchecked[index]"
            :labels="allLabels"
            @checked="saveList"
            @save="saveList"
          />
        </draggable>
      </div>
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
          <div v-for="item in value" :key="item.id" class="small-checkboxes d-flex justify-space-between align-center">
            <v-checkbox v-model="item.checked" hide-details dense :label="item.note" @change="saveList">
              <template #label>
                <div>
                  {{ item.quantity }} <v-icon size="16" class="mx-1"> {{ $globals.icons.close }} </v-icon>
                  {{ item.note }}
                </div>
              </template>
            </v-checkbox>
          </div>
        </div>
      </div>

      <div class="mt-6">
        <v-list-item class="rounded" dense @click="pushNew">
          <v-list-item-icon>
            <v-icon color="info">
              {{ $globals.icons.create }}
            </v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title> {{ $t("general.create") }} </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </div>

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
            <div v-for="item in listItems.checked" :key="item.id" class="d-flex justify-space-between align-center">
              <v-checkbox v-model="item.checked" color="gray" class="my-n2" :label="item.note" @change="saveList">
                <template #label>
                  <div style="text-decoration: line-through">
                    {{ item.quantity }} x
                    {{ item.note }}
                  </div>
                </template>
              </v-checkbox>
            </div>
          </div>
        </v-expand-transition>
      </div>
    </section>

    <!-- Editor -->
    <section v-else>
      <draggable :value="shoppingList.listItems" handle=".handle" @input="updateIndex">
        <div v-for="(item, index) in shoppingList.listItems" :key="index" class="d-flex">
          <div class="number-input-container">
            <v-text-field v-model="shoppingList.listItems[index].quantity" class="mx-1" type="number" label="Qty" />
          </div>
          <v-text-field v-model="item.note" :label="$t('general.name')"> </v-text-field>
          <v-menu offset-x left>
            <template #activator="{ on, attrs }">
              <v-btn icon class="mt-3" v-bind="attrs" v-on="on">
                <v-icon class="handle">
                  {{ $globals.icons.arrowUpDown }}
                </v-icon>
              </v-btn>
            </template>
            <v-list>
              <v-list-item
                v-for="(itm, idx) in contextMenu"
                :key="idx"
                @click="contextMenuAction(itm.action, item, index)"
              >
                <v-list-item-title>{{ itm.title }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
          <div v-if="item.isFood">Is Food</div>
        </div>
      </draggable>

      <v-divider class="my-2" />

      <!-- Create Form -->
      <v-form @submit.prevent="ingredientCreate()">
        <v-checkbox v-model="createIngredient.isFood" label="Treat list item as a recipe ingredient" />
        <div class="d-flex">
          <div class="number-input-container">
            <v-text-field v-model="createIngredient.quantity" class="mx-1" type="number" label="Qty" />
          </div>
          <v-text-field v-model="createIngredient.note" :label="$t('recipe.note')"> </v-text-field>
        </div>
        <div v-if="createIngredient.isFood">Is Food</div>
        <v-autocomplete
          v-model="createIngredient.labelId"
          clearable
          name=""
          :items="allLabels"
          item-value="id"
          item-text="name"
        >
        </v-autocomplete>
        <div class="d-flex justify-end">
          <BaseButton type="submit" create> </BaseButton>
        </div>
      </v-form>
    </section>
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
    <div class="d-flex justify-end mt-10">
      <ButtonLink to="/shopping-lists/labels" text="Manage Labels" :icon="$globals.icons.tags" />
    </div>
  </v-container>
</template>

<script lang="ts">
import draggable from "vuedraggable";

import { defineComponent, useAsync, useRoute, computed, ref } from "@nuxtjs/composition-api";
import { useClipboard, useToggle } from "@vueuse/core";
import { ShoppingListItemCreate } from "~/api/class-interfaces/group-shopping-lists";
import { useUserApi } from "~/composables/api";
import { useAsyncKey, uuid4 } from "~/composables/use-utils";
import { alert } from "~/composables/use-toast";
import { Label } from "~/api/class-interfaces/group-multiple-purpose-labels";
import ShoppingListItem from "~/components/Domain/ShoppingList/ShoppingListItem.vue";
import BannerExperimental from "~/components/global/BannerExperimental.vue";
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
  },
  setup() {
    const userApi = useUserApi();

    const edit = ref(false);
    const byLabel = ref(false);

    const route = useRoute();
    const id = route.value.params.id;

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

    async function saveList() {
      if (!shoppingList.value) {
        return;
      }

      // Set Position
      shoppingList.value.listItems = shoppingList.value.listItems.map((itm: ShoppingListItemCreate, idx: number) => {
        itm.position = idx;
        return itm;
      });

      await userApi.shopping.lists.updateOne(id, shoppingList.value);
      refresh();
      edit.value = false;
    }

    // =====================================
    // Ingredient CRUD

    const listItems = computed(() => {
      return {
        checked: shoppingList.value?.listItems.filter((item) => item.checked),
        unchecked: shoppingList.value?.listItems.filter((item) => !item.checked),
      };
    });

    const createIngredient = ref(ingredientResetFactory());

    function ingredientResetFactory() {
      return {
        id: null,
        shoppingListId: id,
        checked: false,
        position: shoppingList.value?.listItems.length || 1,
        isFood: false,
        quantity: 1,
        note: "",
        unit: null,
        food: null,
        labelId: null,
      };
    }

    function ingredientCreate() {
      const item = { ...createIngredient.value, id: uuid4() };
      shoppingList.value?.listItems.push(item);
      createIngredient.value = ingredientResetFactory();
    }

    function updateIndex(data: ShoppingListItemCreate[]) {
      if (shoppingList.value?.listItems) {
        shoppingList.value.listItems = data;
      }

      if (!edit.value) {
        saveList();
      }
    }

    const [showChecked, toggleShowChecked] = useToggle(false);

    // =====================================
    // Copy List Items

    const { copy, copied, isSupported } = useClipboard();

    function getItemsAsPlain(items: ShoppingListItemCreate[]) {
      return items
        .map((item) => {
          return `${item.quantity} x ${item.unit?.name || ""} ${item.food?.name || ""} ${item.note || ""}`.replace(
            /\s+/g,
            " "
          );
        })
        .join("\n");
    }

    function getItemsAsMarkdown(items: ShoppingListItemCreate[]) {
      return items
        .map((item) => {
          return `- [ ] ${item.quantity} x ${item.unit?.name || ""} ${item.food?.name || ""} ${
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
      const items = shoppingList.value?.listItems.filter((item) => !item.checked);

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
      shoppingList.value?.listItems.forEach((item) => {
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
      const unchecked = shoppingList.value?.listItems.filter((item) => !item.checked);

      if (unchecked?.length === shoppingList.value?.listItems.length) {
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

    function contextMenuAction(action: string, item: ShoppingListItemCreate, idx: number) {
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

    const allLabels = ref([] as Label[]);

    function sortByLabels() {
      byLabel.value = !byLabel.value;
    }

    const presentLabels = computed(() => {
      const labels: PresentLabel[] = [];

      shoppingList.value?.listItems.forEach((item) => {
        if (item.labelId) {
          labels.push({
            // @ts-ignore
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

      shoppingList.value?.listItems.forEach((item) => {
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

    function pushNew() {
      shoppingList.value?.listItems.push(ingredientResetFactory());
    }

    return {
      pushNew,
      itemsByLabel,
      byLabel,
      presentLabels,
      allLabels,
      copyListItems,
      sortByLabels,
      uncheckAll,
      showChecked,
      toggleShowChecked,
      createIngredient,
      contextMenuAction,
      contextMenu,
      deleteChecked,
      listItems,
      updateIndex,
      saveList,
      edit,
      shoppingList,
      ingredientCreate,
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
