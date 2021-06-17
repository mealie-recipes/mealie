<template>
  <v-container>
    <div v-if="selectItems">
      <v-app-bar color="transparent" flat class="mt-n1 rounded">
        <v-icon large left>
          {{ $globals.icons.tags }}
        </v-icon>
        <v-toolbar-title class="headline"> {{ altTitle }} </v-toolbar-title>
        <v-spacer></v-spacer>
      </v-app-bar>
      <v-slide-x-transition hide-on-leave>
        <v-row>
          <v-col cols="12" :sm="12" :md="6" :lg="4" :xl="3" v-for="item in selectItems" :key="item.id">
            <v-card hover :to="`/recipes/${routerTagCat}/${item.slug}`">
              <v-card-actions>
                <v-icon>
                  {{ $globals.icons.tags }}
                </v-icon>
                <v-card-title class="py-1">{{ item.name }}</v-card-title>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-slide-x-transition>
    </div>
    <CardSection v-else :sortable="true" :title="title" :recipes="shownRecipes" @sort="assignSorted" />
  </v-container>
</template>

<script>
import { api } from "@/api";
import CardSection from "@/components/UI/CardSection";
export default {
  components: {
    CardSection,
  },
  data() {
    return {
      title: "",
      recipes: [],
      sortedResults: [],
    };
  },
  computed: {
    currentCategory() {
      return this.$route.params.category || false;
    },
    currentTag() {
      return this.$route.params.tag || false;
    },
    TagOrCategory() {
      return this.currentCategory || this.currentTag;
    },
    routerTagCat() {
      return this.$route.path.split("/")[2];
    },
    altTitle() {
      return this.routerTagCat === "category" ? this.$t("recipe.categories") : this.$t("tag.tags");
    },

    selectItems() {
      if (this.TagOrCategory) return false;
      if (this.routerTagCat === "category") {
        return this.$store.getters.getAllCategories;
      }
      return this.$store.getters.getAllTags;
    },

    shownRecipes() {
      if (this.sortedResults.length > 0) {
        return this.sortedResults;
      } else {
        return this.recipes;
      }
    },
  },
  watch: {
    async TagOrCategory() {
      this.sortedResults = [];
      this.getRecipes();
    },
  },
  mounted() {
    this.getRecipes();
    this.sortedResults = [];
  },
  methods: {
    async getRecipes() {
      if (!this.TagOrCategory === null || this.selectItems) return;

      let data = {};
      if (this.currentCategory) {
        data = await api.categories.getRecipesInCategory(this.TagOrCategory);
      } else {
        data = await api.tags.getRecipesInTag(this.TagOrCategory);
      }
      this.title = data.name;
      this.recipes = data.recipes;
    },
    assignSorted(val) {
      this.sortedResults = val.slice();
    },
  },
};
</script>

<style></style>
