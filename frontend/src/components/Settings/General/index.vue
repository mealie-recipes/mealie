<template>
  <v-card>
    <v-card-title> General Settings </v-card-title>
    <v-divider></v-divider>
    <v-card-text>
      <v-row>
        <v-col>
          <v-select
            v-model="selectedLang"
            :items="langOptions"
            item-text="name"
            item-value="value"
            label="Language"
          >
          </v-select>
        </v-col>
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
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
  },
};
</script>

<style>
</style>