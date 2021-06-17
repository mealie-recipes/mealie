<template>
  <v-card outlined class="mt-n1">
    <BaseDialog
      ref="renameDialog"
      :title-icon="$globals.icons.tags"
      :title="renameTarget.title"
      :submit-text="$t('general.update')"
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
          {{ $tc("settings.toolbox.recipes-affected", renameTarget.recipes.length || 0) }}
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
    </BaseDialog>

    <div class="d-flex justify-center align-center pa-2 flex-wrap">
      <NewCategoryTagDialog ref="newDialog" :tag-dialog="isTags">
        <v-btn @click="openNewDialog" small color="success" class="mr-1 mb-1">
          {{ $t("general.create") }}
        </v-btn>
      </NewCategoryTagDialog>

      <BulkAssign isTags="isTags" class="mr-1 mb-1" />

      <v-btn @click="titleCaseAll" small color="success" class="mr-1 mb-1" :loading="loadingTitleCase">
        {{ $t("settings.toolbox.title-case-all") }}
      </v-btn>
      <RemoveUnused :isTags="isTags" class="mb-1" />

      <v-spacer v-if="!isMobile"> </v-spacer>

      <fuse-search-bar class="fit-search mr-2" :raw-data="allItems" @results="filterItems" :search="searchString">
        <v-text-field
          v-model="searchString"
          clearable
          solo
          dense
          class="mx-2"
          hide-details
          single-line
          :placeholder="$t('search.search')"
          :prepend-inner-icon="$globals.icons.search"
        >
        </v-text-field>
      </fuse-search-bar>
    </div>
    <v-divider></v-divider>

    <v-card-text>
      <v-row>
        <v-col cols="12" :sm="12" :md="6" :lg="4" :xl="3" v-for="item in results" :key="item.id">
          <v-card>
            <v-card-title class="py-1">{{ item.name }}</v-card-title>
            <v-divider class="mx-2"></v-divider>
            <v-card-actions>
              <ConfirmationDialog
                :title="$t('general.confirm') + ' ' + $t('general.delete')"
                :icon="$globals.icons.tags"
                :message="$t('general.confirm-delete-generic')"
                @confirm="deleteItem(item.slug)"
              >
                <template v-slot="{ open }">
                  <TheButton minor small delete @click="open"></TheButton>
                </template>
              </ConfirmationDialog>
              <v-spacer></v-spacer>
              <TheButton small edit @click="openEditDialog(item)" />
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
import ConfirmationDialog from "@/components/UI/Dialogs/ConfirmationDialog.vue";
import TheButton from "@/components/UI/Buttons/TheButton.vue";
export default {
  mixins: [validators],
  components: {
    BaseDialog,
    MobileRecipeCard,
    FuseSearchBar,
    RemoveUnused,
    NewCategoryTagDialog,
    BulkAssign,
    ConfirmationDialog,
    TheButton,
  },
  props: {
    isTags: {
      default: true,
    },
  },
  data() {
    return {
      loadingTitleCase: false,
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
    isMobile() {
      return this.$vuetify.breakpoint.name === "xs";
    },
    allItems() {
      return this.isTags ? this.$store.getters.getAllTags : this.$store.getters.getAllCategories;
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
        title: this.$t("general.rename-object", [item.name]),
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
    async renameFromDialog(name, newName) {
      if (this.$refs.renameForm.validate()) {
        await this.rename(name, newName);
      }
      this.$refs.renameDialog.close();
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
      this.loadingTitleCase = true;
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
      this.loadingTitleCase = false;
    },
  },
};
</script>

<style>
.overflow-fix .v-toolbar__content {
  height: auto !important;
  flex-wrap: wrap;
}
.fit-search {
  max-width: 300px;
}
</style>
