<template>
  <v-card flat>
    <v-card-text>
      <h2 class="mt-1 mb-1">Home Page</h2>
      <v-row align="center" justify="center" dense class="mb-n7 pb-n5">
        <v-col sm="2">
          <v-switch v-model="showRecent" label="Show Recent"></v-switch>
        </v-col>
        <v-col>
          <v-slider
            class="pt-4"
            label="Card Per Section"
            v-model="showLimit"
            max="30"
            dense
            color="primary"
            min="3"
            thumb-label
          >
          </v-slider>
        </v-col>
        <v-spacer></v-spacer>
      </v-row>
    </v-card-text>
    <v-card-text>
      <v-row>
        <v-col>
          <v-card outlined min-height="250">
            <v-card-text class="pt-2 pb-1">
              <h3>Homepage Categories</h3>
            </v-card-text>
            <v-divider></v-divider>
            <v-list min-height="200px" dense>
              <v-list-item-group>
                <draggable v-model="homeCategories" group="categories">
                  <v-list-item
                    v-for="(item, index) in homeCategories"
                    :key="item"
                  >
                    <v-list-item-icon>
                      <v-icon>mdi-menu</v-icon>
                    </v-list-item-icon>

                    <v-list-item-content>
                      <v-list-item-title v-text="item"></v-list-item-title>
                    </v-list-item-content>
                    <v-list-item-icon @click="deleteActiveCategory(index)">
                      <v-icon>mdi-delete</v-icon>
                    </v-list-item-icon>
                  </v-list-item>
                </draggable>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-col>
        <v-col>
          <v-card outlined min-height="250px">
            <v-card-text class="pt-2 pb-1">
              <h3>
                All Categories
                <span>
                  <v-btn absolute right x-small color="success" icon> <v-icon>mdi-plus</v-icon></v-btn>
                </span>
              </h3>
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
                    <v-list-item-icon @click="deleteActiveCategory(index)">
                      <v-icon>mdi-delete</v-icon>
                    </v-list-item-icon>
                  </v-list-item>
                </draggable>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="success" @click="saveSettings" class="mr-2">
        <v-icon left> mdi-content-save </v-icon>
        {{ $t("general.save") }}
      </v-btn>
    </v-card-actions>
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
      homeCategories: [],
      showLimit: null,
      categories: ["breakfast"],
      showRecent: true,
    };
  },
  mounted() {
    this.getOptions();
  },

  methods: {
    getOptions() {
      let options = this.$store.getters.getHomePageSettings;
      this.showLimit = options.showLimit;
      this.categories = options.categories;
      this.showRecent = options.showRecent;
      this.homeCategories = options.homeCategories;
    },
    deleteActiveCategory(index) {
      this.homeCategories.splice(index, 1);
    },
    saveSettings() {
      let payload = {
        showRecent: this.showRecent,
        showLimit: this.showLimit,
        categories: this.categories,
        homeCategories: this.homeCategories,
      };

      this.$store.commit("setHomePageSettings", payload);
    },
  },
};
</script>

<style>
</style>