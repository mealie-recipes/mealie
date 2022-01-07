<template>
  <v-container v-if="shoppingList" class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/shopping-cart.svg')"></v-img>
      </template>
      <template #title> {{ shoppingList.name }} </template>
    </BasePageTitle>
    <div class="d-flex justify-end my-4">
      <BaseButton v-if="!edit" edit @click="edit = true" />
      <BaseButton v-else save @click="saveList" />
    </div>

    <!-- Viewer -->
    <section v-if="!edit">
      <div>
        <draggable :value="shoppingList.listItems" handle=".handle" @input="updateIndex">
          <div v-for="item in listItems.unchecked" :key="item.id" class="d-flex justify-space-between align-center">
            <v-checkbox v-model="item.checked" class="my-n2" :label="item.note" @change="saveList">
              <template #label>
                <div>
                  {{ item.quantity }} <v-icon size="16" class="mx-1"> {{ $globals.icons.close }} </v-icon>
                  {{ item.note }}
                </div>
              </template>
            </v-checkbox>
            <v-icon class="handle">
              {{ $globals.icons.arrowUpDown }}
            </v-icon>
          </div>
        </draggable>
      </div>
      <div v-if="listItems.checked && listItems.checked.length > 0" class="mt-6">
        <v-divider class="my-4"></v-divider>
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
        <div class="d-flex">
          <BaseButton small delete class="ml-auto" @click="deleteChecked"> Delete Checked </BaseButton>
        </div>
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
      <v-form @submit.prevent="ingredientCreate()">
        <v-checkbox v-model="createIngredient.isFood" label="Treat list item as a recipe ingredient" />

        <div class="d-flex">
          <div class="number-input-container">
            <v-text-field v-model="createIngredient.quantity" class="mx-1" type="number" label="Qty" />
          </div>
          <v-text-field v-model="createIngredient.note" :label="$t('recipe.note')"> </v-text-field>
        </div>
        <div v-if="createIngredient.isFood">Is Food</div>
        <div class="d-flex justify-end">
          <BaseButton type="submit" create> </BaseButton>
        </div>
      </v-form>
    </section>
  </v-container>
</template>

<script lang="ts">
import draggable from "vuedraggable";

import { defineComponent, reactive, useAsync, useRoute, toRefs, computed, ref } from "@nuxtjs/composition-api";
import { ShoppingListItemCreate } from "~/api/class-interfaces/group-shopping-lists";
import { useUserApi } from "~/composables/api";
import { useAsyncKey, uuid4 } from "~/composables/use-utils";

export default defineComponent({
  components: {
    draggable,
  },
  setup() {
    const userApi = useUserApi();

    const state = reactive({
      edit: false,
    });

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
      state.edit = false;
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

      if (!state.edit) {
        saveList();
      }
    }

    async function deleteChecked() {
      const unchecked = shoppingList.value?.listItems.filter((item) => !item.checked);

      if (shoppingList.value?.listItems) {
        shoppingList.value.listItems = unchecked || [];
      }

      await saveList();
    }

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

    return {
      createIngredient,
      contextMenuAction,
      contextMenu,
      deleteChecked,
      listItems,
      updateIndex,
      saveList,
      ...toRefs(state),
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
