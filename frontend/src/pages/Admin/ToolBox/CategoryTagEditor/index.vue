<template>
  <v-card outlined class="mt-n1">
    <base-dialog
      ref="renameDialog"
      title-icon="mdi-tag"
      :title="renameTarget.title"
      modal-width="800"
      @submit="renameFromDialog(renameTarget.slug, renameTarget.newName)"
    >
      <v-form ref="renameForm">
        <v-card-text>
          <v-text-field
            :placeholder="$t('settings.toolbox.new-name')"
            :rules="[existsRule]"
            v-model="renameTarget.newName"
          ></v-text-field>
        </v-card-text>
      </v-form>
      <template slot="below-actions">
        <v-card-title class="headline">
          {{ renameTarget.recipes.length || 0 }} Recipes Effected
        </v-card-title>
        <MobileRecipeCard
          class="ml-2 mr-2 mt-2 mb-2"
          v-for="recipe in renameTarget.recipes"
          :key="recipe.slug"
          :slug="recipe.slug"
          :name="recipe.name"
          :description="recipe.description"
          :rating="recipe.rating"
          :route="false"
          :tags="recipe.tags"
        />
      </template>
    </base-dialog>

    <v-app-bar flat color="white">
      <new-category-tag-dialog
        ref="newDialog"
        :tag-dialog="isTags"
        class="mr-1"
      >
        <v-btn @click="openNewDialog" small color="success">
          New
        </v-btn>
      </new-category-tag-dialog>
      <BulkAssign isTags="isTags" />
      <v-btn @click="titleCaseAll" class="mr-1" small color="success">
        Title Case All
      </v-btn>
      <RemoveUnused :isTags="isTags" />
      <v-spacer> </v-spacer>
      <fuse-search-bar
        :raw-data="allItems"
        @results="filterItems"
        :search="searchString"
      >
        <v-text-field
          v-model="searchString"
          clearable
          solo
          dense
          class="mx-2"
          hide-details
          single-line
          :placeholder="$t('search.search')"
          prepend-inner-icon="mdi-magnify"
        >
        </v-text-field>
      </fuse-search-bar>
    </v-app-bar>
    <v-divider></v-divider>

    <v-card-text>
      <v-row>
        <v-col
          :sm="6"
          :md="6"
          :lg="4"
          :xl="3"
          v-for="item in results"
          :key="item.id"
        >
          <v-card>
            <v-card-actions>
              <v-card-title class="py-1">{{ item.name }}</v-card-title>
              <v-spacer></v-spacer>
              <v-btn small text color="info" @click="openEditDialog(item)">
                Edit
              </v-btn>
              <v-btn small text color="error" @click="deleteItem(item.slug)"
                >Delete
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import FuseSearchBar from "@/components/UI/Search/FuseSearchBar";
import MobileRecipeCard from "@/components/Recipe/MobileRecipeCard";
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import { api } from "@/api";
import { validators } from "@/mixins/validators";
import RemoveUnused from "./RemoveUnused";
import BulkAssign from "./BulkAssign";
import NewCategoryTagDialog from "@/components/UI/Dialogs/NewCategoryTagDialog";
export default {
  mixins: [validators],
  components: {
    BaseDialog,
    MobileRecipeCard,
    FuseSearchBar,
    RemoveUnused,
    NewCategoryTagDialog,
    BulkAssign,
  },
  props: {
    isTags: {
      default: true,
    },
  },
  data() {
    return {
      searchString: "",
      searchResults: [],
      renameTarget: {
        title: "",
        name: "",
        slug: "",
        newName: "",
        recipes: [],
      },
    };
  },
  computed: {
    allItems() {
      return this.isTags
        ? this.$store.getters.getAllTags
        : this.$store.getters.getAllCategories;
    },
    results() {
      if (this.searchString != null && this.searchString.length >= 1) {
        return this.searchResults;
      }
      return this.allItems;
    },
  },
  methods: {
    filterItems(val) {
      this.searchResults = val.map(x => x.item);
    },
    openNewDialog() {
      this.$refs.newDialog.open();
    },
    async openEditDialog(item) {
      let fromAPI = {};
      if (this.isTags) {
        fromAPI = await api.tags.getRecipesInTag(item.slug);
      } else {
        fromAPI = await api.categories.getRecipesInCategory(item.slug);
      }

      this.renameTarget = {
        title: `Rename ${item.name}`,
        name: item.name,
        slug: item.slug,
        newName: "",
        recipes: fromAPI.recipes,
      };

      this.$refs.renameDialog.open();
    },
    async deleteItem(name) {
      if (this.isTags) {
        await api.tags.delete(name);
      } else {
        await api.categories.delete(name);
      }
    },
    renameFromDialog(name, newName) {
      if (this.$refs.renameForm.validate()) {
        this.rename(name, newName);
      }
    },
    async rename(name, newName) {
      if (this.isTags) {
        await api.tags.update(name, newName);
      } else {
        await api.categories.update(name, newName);
      }
    },
    titleCase(lowerName) {
      return lowerName.replace(/(?:^|\s|-)\S/g, x => x.toUpperCase());
    },
    async titleCaseAll() {
      const renameList = this.allItems.map(x => ({
        slug: x.slug,
        name: x.name,
        newName: this.titleCase(x.name),
      }));

      if (this.isTags) {
        renameList.forEach(async element => {
          if (element.name === element.newName) return;
          await api.tags.update(element.slug, element.newName, true);
        });
        this.$store.dispatch("requestTags");
      } else {
        renameList.forEach(async element => {
          if (element.name === element.newName) return;
          await api.categories.update(element.slug, element.newName, true);
        });
        this.$store.dispatch("requestCategories");
      }
    },
  },
};
</script>

<style lang="scss" scoped>
</style>