<template>
  <v-container>
    <v-app-bar color="transparent" flat class="mt-n1 rounded">
      <v-btn v-if="list" color="info" @click="list = null">
        <v-icon left>
          mdi-arrow-left-bold
        </v-icon>
        All Lists
      </v-btn>
      <v-icon v-if="!list" large left>
        mdi-format-list-checks
      </v-icon>
      <v-toolbar-title v-if="!list" class="headline"> Shopping Lists </v-toolbar-title>
      <v-spacer></v-spacer>
      <BaseDialog title="New List" title-icon="mdi-format-list-checks" submit-text="Create" @submit="createNewList">
        <template v-slot:open="{ open }">
          <v-btn color="info" @click="open">
            <v-icon left>
              {{ $globals.icons.create }}
            </v-icon>
            New List
          </v-btn>
        </template>

        <v-card-text>
          <v-text-field autofocus v-model="newList.name" label="List Name"> </v-text-field>
        </v-card-text>
      </BaseDialog>
    </v-app-bar>

    <v-slide-x-transition hide-on-leave>
      <v-row v-if="list == null">
        <v-col cols="12" :sm="6" :md="6" :lg="4" :xl="3" v-for="(item, index) in group.shoppingLists" :key="index">
          <v-card>
            <v-card-title class="headline">
              {{ item.name }}
            </v-card-title>
            <v-divider class="mx-2"></v-divider>
            <v-card-actions>
              <v-btn text color="error" @click="deleteList(item.id)">
                <v-icon left>
                  {{ $globals.icons.delete }}
                </v-icon>
                Delete
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn color="info" @click="list = item.id">
                <v-icon left>
                  mdi-cart-check
                </v-icon>
                View
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <v-card v-else-if="activeList">
        <v-card-title class="headline">
          <TheCopyButton v-if="!edit" :copy-text="listAsText" color="info" />
          <v-text-field label="Name" single-line dense v-if="edit" v-model="activeList.name"> </v-text-field>
          <div v-else>
            {{ activeList.name }}
          </div>
          <v-spacer></v-spacer>
          <v-btn v-if="edit" color="success" @click="saveList">
            Save
          </v-btn>
          <v-btn v-else color="info" @click="edit = true">
            Edit
          </v-btn>
        </v-card-title>
        <v-divider class="mx-2 mb-1"></v-divider>

        <SearchDialog ref="searchRecipe" @select="importIngredients" />
        <v-card-text>
          <v-row dense v-for="(item, index) in activeList.items" :key="index">
            <v-col v-if="edit" cols="12" class="d-flex no-wrap align-center">
              <p class="mb-0">Quantity: {{ item.quantity }}</p>
              <div v-if="edit">
                <v-btn x-small text class="ml-1" @click="activeList.items[index].quantity -= 1">
                  <v-icon>
                    mdi-minus
                  </v-icon>
                </v-btn>
                <v-btn x-small text class="mr-1" @click="activeList.items[index].quantity += 1">
                  <v-icon>
                    {{ $globals.icons.create }}
                  </v-icon>
                </v-btn>
              </div>
              <v-spacer></v-spacer>
              <v-btn v-if="edit" icon @click="removeItemByIndex(index)" color="error">
                <v-icon>{{ $globals.icons.delete }}</v-icon>
              </v-btn>
            </v-col>

            <v-col cols="12" class="d-flex no-wrap align-center">
              <v-checkbox
                v-if="!edit"
                hide-details
                v-model="activeList.items[index].checked"
                class="pt-0 my-auto py-auto"
                color="secondary"
                @change="saveList"
              ></v-checkbox>

              <p v-if="!edit" class="mb-0">{{ item.quantity }}</p>

              <v-icon v-if="!edit" small class="mx-3">
                mdi-window-close
              </v-icon>

              <vue-markdown v-if="!edit" class="dense-markdown" :source="item.text"> </vue-markdown>
              <v-textarea
                single-line
                rows="1"
                auto-grow
                class="mb-n2 pa-0"
                dense
                v-else
                v-model="activeList.items[index].text"
              ></v-textarea>
            </v-col>
            <v-divider class="ma-1"></v-divider>
          </v-row>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn v-if="edit" color="success" @click="openSearch">
            <v-icon left>
              {{ $globals.icons.primary }}
            </v-icon>
            From Recipe
          </v-btn>
          <v-btn v-if="edit" color="success" @click="newItem">
            <v-icon left>
              {{ $globals.icons.create }}
            </v-icon>
            New
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-slide-x-transition>
  </v-container>
</template>

<script>
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import SearchDialog from "@/components/UI/Search/SearchDialog";
import TheCopyButton from "@/components/UI/Buttons/TheCopyButton";
import VueMarkdown from "@adapttive/vue-markdown";
import { api } from "@/api";
export default {
  components: {
    BaseDialog,
    SearchDialog,
    TheCopyButton,
    VueMarkdown,
  },
  data() {
    return {
      newList: {
        name: "",
        group: "",
        items: [],
      },
      activeList: null,

      edit: false,
    };
  },
  computed: {
    group() {
      return this.$store.getters.getCurrentGroup;
    },
    list: {
      set(list) {
        this.$router.replace({ query: { ...this.$route.query, list } });
      },
      get() {
        return this.$route.query.list;
      },
    },
    listAsText() {
      const formatList = this.activeList.items.map(x => {
        return `${x.quantity} - ${x.text}`;
      });

      return formatList.join("\n");
    },
  },
  watch: {
    group: {
      immediate: true,
      handler: "setActiveList",
    },
    list: {
      immediate: true,
      handler: "setActiveList",
    },
  },
  methods: {
    openSearch() {
      this.$refs.searchRecipe.open();
    },
    async importIngredients(_, slug) {
      const recipe = await api.recipes.requestDetails(slug);

      const ingredients = recipe.recipeIngredient.map(x => ({
        title: "",
        text: x,
        quantity: 1,
        checked: false,
      }));

      this.activeList.items = [...this.activeList.items, ...ingredients];
      this.consolidateList();
    },
    consolidateList() {
      const allText = this.activeList.items.map(x => x.text);

      const uniqueText = allText.filter((item, index) => {
        return allText.indexOf(item) === index;
      });

      const newItems = uniqueText.map(x => {
        let matchingItems = this.activeList.items.filter(y => y.text === x);
        matchingItems[0].quantity = this.sumQuantiy(matchingItems);
        return matchingItems[0];
      });

      this.activeList.items = newItems;
    },
    sumQuantiy(itemList) {
      let quantity = 0;
      itemList.forEach(element => {
        quantity += element.quantity;
      });
      return quantity;
    },
    setActiveList() {
      if (!this.list) return null;
      if (!this.group.shoppingLists) return null;
      this.activeList = this.group.shoppingLists.find(x => x.id == this.list);
    },
    async createNewList() {
      this.newList.group = this.group.name;

      await api.shoppingLists.createShoppingList(this.newList);

      this.$store.dispatch("requestCurrentGroup");
    },
    async deleteList(id) {
      await api.shoppingLists.deleteShoppingList(id);
      this.$store.dispatch("requestCurrentGroup");
    },
    removeItemByIndex(index) {
      this.activeList.items.splice(index, 1);
    },
    newItem() {
      this.activeList.items.push({
        title: null,
        text: "",
        quantity: 1,
        checked: false,
      });
    },
    async saveList() {
      await this.consolidateList();
      await api.shoppingLists.updateShoppingList(this.activeList.id, this.activeList);
      this.edit = false;
    },
  },
};
</script>

<style >
</style>