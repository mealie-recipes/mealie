<template>
  <v-container>
    <CategorySidebar />
    <v-card flat height="100%">
      <v-card-title class="text-center justify-center py-6 headline">
        Category Section
      </v-card-title>
      <div v-if="render">
        <v-tabs v-model="tab" background-color="transparent" grow>
          <v-tab v-for="item in categories" :key="item.slug">
            {{ item.name }}
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="tab">
          <v-tab-item
            v-for="(item, index) in categories"
            :key="item.slug + index"
          >
            <CardSection class="mb-5 mx-1" :recipes="filterRecipe(item.slug)" />
          </v-tab-item>
        </v-tabs-items>
      </div>
    </v-card>
  </v-container>
</template>

<script>
import CardSection from "@/components/UI/CardSection";
import CategorySidebar from "@/components/UI/CategorySidebar";
import api from "@/api";

export default {
  components: {
    CardSection,
    CategorySidebar,
  },
  data() {
    return {
      tab: null,
      render: false,
      recipeStore: [],
      categories: [
        {
          id: 2,
          slug: "brownie",
          name: "brownie",
        },
        {
          id: 3,
          slug: "dessert",
          name: "dessert",
        },
        {
          id: 4,
          slug: "drink",
          name: "Drink",
        },
      ],
    };
  },

  watch: {
    tab(val) {
      console.log(val);
    },
  },
  async mounted() {
    await this.buildPage();
    this.render = true;
  },
  methods: {
    async buildPage() {
      this.categories.forEach(async element => {
        let categoryRecipes = await this.getRecipeByCategory(element.slug);
        this.recipeStore.push(categoryRecipes);
      });
    },
    async getRecipeByCategory(category) {
      return await api.categories.get_recipes_in_category(category);
    },
    filterRecipe(slug) {
      const storeCategory = this.recipeStore.find(
        element => element.slug === slug
      );
      return storeCategory ? storeCategory.recipes : [];
    },
  },
};
</script>

<style>
</style>