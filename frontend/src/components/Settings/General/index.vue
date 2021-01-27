<template>
  <v-card>
    <v-card-title>
      General Settings
      <v-spacer></v-spacer>
      <span>
        <v-btn class="pt-1" text to="/docs">
          <v-icon left>mdi-link</v-icon>
          Local API
        </v-btn>
      </span>
    </v-card-title>
    <v-divider></v-divider>
    <v-card-text>
      <h2 class="mt-1 mb-1">Home Page</h2>
      <v-slider
        label="Card Per Section"
        v-model="homeOptions.recipesToShow"
        max="30"
        dense
        color="primary"
        min="3"
        thumb-label
      >
      </v-slider>
    </v-card-text>
    <v-card-text>
      <v-row>
        <v-col>
          <v-card outlined min-height="250">
            <v-card-text class="pb-1">
              <h3>Homepage Categories</h3>
            </v-card-text>
            <v-divider></v-divider>
            <v-list min-height="200px" dense>
              <v-list-item-group>
                <draggable v-model="usedCategories" group="categories">
                  <v-list-item v-for="item in usedCategories" :key="item">
                    <v-list-item-icon>
                      <v-icon>mdi-menu</v-icon>
                    </v-list-item-icon>

                    <v-list-item-content>
                      <v-list-item-title v-text="item"></v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </draggable>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-col>
        <v-col>
          <v-card outlined min-height="250px">
            <v-card-text class="pb-1">
              <h3>All Categories</h3>
            </v-card-text>
            <v-divider></v-divider>
            <v-list min-height="200px" dense>
              <v-list-item-group>
                <draggable v-model="categories" group="categories">
                  <v-list-item v-for="item in categories" :key="item">
                    <v-list-item-icon>
                      <v-icon>mdi-menu</v-icon>
                    </v-list-item-icon>

                    <v-list-item-content>
                      <v-list-item-title v-text="item"></v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </draggable>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-col>
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
import draggable from "vuedraggable";

export default {
  components: {
    draggable,
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