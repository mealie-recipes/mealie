<template>
  <v-card>
    <v-card-title class="headline">
      {{ $t("settings.admin-settings") }}
      <v-spacer></v-spacer>
      <span>
        <v-btn class="pt-1" text href="/docs">
          {{ $t("settings.local-api") }}
          <v-icon right>mdi-open-in-new</v-icon>
        </v-btn>
      </span>
    </v-card-title>

    <v-divider></v-divider>
    <HomePageSettings />
    <v-divider></v-divider>
  </v-card>
</template>

<script>
import HomePageSettings from "@/components/Admin/General/HomePageSettings";

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