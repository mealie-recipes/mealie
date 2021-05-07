<template>
  <v-container>
    <v-card flat height="100%">
      <v-app-bar color="transparent" flat class="mt-n1 rounded">
        <v-icon large left>
          mdi-tag-multiple-outline
        </v-icon>
        <v-toolbar-title class="headline"> {{ page.name }} </v-toolbar-title>
      </v-app-bar>

      <div v-if="render">
        <v-tabs v-model="tab" background-color="transparent" grow>
          <v-tab v-for="item in page.categories" :key="item.slug" :href="`#${item.slug}`">
            {{ item.name }}
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="tab">
          <v-tab-item v-for="(item, index) in page.categories" :key="item.slug + index" :value="item.slug">
            <CardSection class="mb-5 mx-1" :recipes="item.recipes" @sort="sortRecipes($event, index)" />
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
      page: "",
      title: "",
      render: false,
      recipeStore: [],
      categories: [],
    };
  },
  computed: {
    pageSlug() {
      return this.$route.params.customPage;
    },
    tab: {
      set(tab) {
        this.$router.replace({ query: { ...this.$route.query, tab } });
      },
      get() {
        return this.$route.query.tab;
      },
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
      this.page = await api.siteSettings.getPage(this.pageSlug);
    },
    filterRecipe(slug) {
      const storeCategory = this.recipeStore.find(element => element.slug === slug);
      return storeCategory ? storeCategory.recipes : [];
    },
    sortRecipes(sortedRecipes, destKey) {
      this.page.categories[destKey].recipes = sortedRecipes;
    },
  },
};
</script>
