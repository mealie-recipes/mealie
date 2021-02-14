<template>
  <v-card>
    <v-card-title>
      {{ $t("settings.general-settings") }}
      <v-spacer></v-spacer>
      <span>
        <v-btn class="pt-1" text href="/docs">
          {{ $t("settings.local-api") }}
          <v-icon right>mdi-open-in-new</v-icon>
        </v-btn>
      </span>
    </v-card-title>
    <v-divider></v-divider>
    <v-card-text>
      <h2 class="mt-1 mb-4">{{ $t("settings.language") }}</h2>
      <v-row>
        <v-col cols="3">
          <v-select
            dense
            v-model="selectedLang"
            :items="langOptions"
            item-text="name"
            item-value="value"
            :label="$t('settings.language')"
          >
          </v-select>
        </v-col>
      </v-row>
    </v-card-text>
    <v-divider></v-divider>
    <HomePageSettings />
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
      langOptions: [],
      selectedLang: "en",
    };
  },
  mounted() {
    this.getOptions();
  },
  watch: {
    selectedLang() {
      this.$store.commit("setLang", this.selectedLang);
    },
  },
  methods: {
    getOptions() {
      this.langOptions = this.$store.getters.getAllLangs;
      this.selectedLang = this.$store.getters.getActiveLang;
    },
    removeCategory(index) {
      this.value.categories.splice(index, 1);
    },
  },
};
</script>

<style>
</style>