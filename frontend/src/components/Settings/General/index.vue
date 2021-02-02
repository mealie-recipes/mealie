<template>
  <v-card>
    <v-card-title>
      {{ $t("settings.general-settings") }}
      <v-spacer></v-spacer>
      <span>
        <v-btn class="pt-1" text href="/docs">
          <v-icon left>mdi-link</v-icon>
          {{ $t("settings.local-api") }}
        </v-btn>
      </span>
    </v-card-title>
    <v-divider></v-divider>
    <HomePageSettings />
    <v-divider></v-divider>
    <v-card-text>
      <h2 class="mt-1 mb-1">{{ $t("settings.language") }}</h2>
      <v-row>
        <v-col>
          <v-select
            v-model="selectedLang"
            :items="langOptions"
            item-text="name"
            item-value="value"
            :label="$t('settings.language')"
          >
          </v-select>
        </v-col>
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
      </v-row>
    </v-card-text>
    <v-divider></v-divider>
  </v-card>
</template>

<script>
import HomePageSettings from "./HomePageSettings";

export default {
  components: {
    HomePageSettings,
  },
  data() {
    return {
      categories: ["cat 1", "cat 2", "cat 3"],
      usedCategories: ["recent"],
      langOptions: [],
      selectedLang: "en",
      homeOptions: {
        recipesToShow: 10,
      },
    };
  },
  mounted() {
    this.getOptions();
  },
  watch: {
    usedCategories() {
      console.log(this.usedCategories);
    },
    selectedLang() {
      this.$store.commit("setLang", this.selectedLang);
    },
  },
  methods: {
    getOptions() {
      this.langOptions = this.$store.getters.getAllLangs;
      this.selectedLang = this.$store.getters.getActiveLang;
    },
  },
};
</script>

<style>
</style>