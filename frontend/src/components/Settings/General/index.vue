<template>
  <v-card>
    <v-card-title> General Settings </v-card-title>
    <v-divider></v-divider>
    <v-card-text>
      <h2 class="mt-1 mb-1">Home Page</h2>
      <v-row>
        <v-col> Section Selector </v-col>
        <v-col cols="2">
          <v-text-field label="Card Limit"></v-text-field>
        </v-col>
        <v-spacer> </v-spacer>
        <v-spacer> </v-spacer>
      </v-row>
    </v-card-text>
    <v-divider></v-divider>
    <v-card-text>
      <h2 class="mt-1 mb-1">Language</h2>
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
    <v-divider></v-divider>
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