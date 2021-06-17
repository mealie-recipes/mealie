<template>
  <v-container>
    <v-text-field v-model="testUrl" outlined single-line label="Recipe Url"> </v-text-field>
    <div class="d-flex">
      <v-btn class="mt-0 ml-auto" color="info" @click="getTestData">
        <v-icon left> {{ $globals.icons.testTube }} </v-icon>
        Test Scrape
      </v-btn>
    </div>
    <VJsoneditor class="mt-2" v-model="recipeJson" height="1500px" :options="jsonEditorOptions" />
  </v-container>
</template>

<script>
import { api } from "@/api";
export default {
  components: {
    VJsoneditor: () => import(/* webpackChunkName: "json-editor" */ "v-jsoneditor"),
  },
  data() {
    return {
      jsonEditorOptions: {
        mode: "code",
        search: false,
        mainMenuBar: false,
      },
      recipeJson: {},
      defaultMessage: { details: "site failed to return valid schema" },
    };
  },
  mounted() {
    if (this.$route.query.test_url) {
      this.getTestData();
    }
  },
  computed: {
    testUrl: {
      set(test_url) {
        this.$router.replace({ query: { ...this.$route.query, test_url } });
      },
      get() {
        return this.$route.query.test_url || "";
      },
    },
  },
  methods: {
    async getTestData() {
      const response = await api.recipes.testScrapeURL(this.testUrl).catch(() => {
        this.recipeJson = this.defaultMessage;
      });

      if (response.length < 1) {
        this.recipeJson = this.defaultMessage;
        return;
      }

      this.recipeJson = response;
    },
  },
};
</script>
