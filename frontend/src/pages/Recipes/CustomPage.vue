<template>
  <v-container>
    <v-card flat height="100%">
      <v-app-bar flat>
        <v-spacer></v-spacer>
        <v-card-title class="text-center justify-center py-3 ">
          {{ title.toUpperCase() }}
        </v-card-title>
        <v-spacer></v-spacer>
      </v-app-bar>

      <div v-if="render">
        <v-tabs v-model="tab" background-color="transparent" grow>
          <v-tab v-for="item in categories" :key="item.slug">
            {{ item.name }}
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="tab">
          <v-tab-item v-for="(item, index) in categories" :key="item.slug + index">
            <CardSection class="mb-5 mx-1" :recipes="filterRecipe(item.slug)" />
          </v-tab-item>
        </v-tabs-items>
      </div>
    </v-card>
  </v-container>
</template>

<script>
import CardSection from "@/components/UI/CardSection";
import { api } from "@/api";

export default {
  components: {
    CardSection,
  },
  data() {
    return {
      title: "",
      tab: null,
      render: false,
      recipeStore: [],
      categories: [],
    };
  },
  computed: {
    pageSlug() {
      return this.$route.params.customPage;
    },
  },

  watch: {
    pageSlug() {
      this.buildPage();
    },
  },

  async mounted() {
    await this.buildPage();
    this.render = true;
  },
  methods: {
    async buildPage() {
      const page = await api.siteSettings.getPage(this.pageSlug);
      this.title = page.name;
      this.categories = page.categories;
      page.categories.forEach(async element => {
        let categoryRecipes = await this.getRecipeByCategory(element.slug);
        this.recipeStore.push(categoryRecipes);
      });
    },
    async getRecipeByCategory(category) {
      return await api.categories.getRecipesInCategory(category);
    },
    filterRecipe(slug) {
      const storeCategory = this.recipeStore.find(element => element.slug === slug);
      return storeCategory ? storeCategory.recipes : [];
    },
  },
};
</script>

<style>
.header-background {
  background-color: #121619;
}
</style>
