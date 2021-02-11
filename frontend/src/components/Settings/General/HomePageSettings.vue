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
            <v-list
              min-height="200"
              dense
              max-height="200"
              style="overflow:auto"
            >
              <v-list-item-group>
                <draggable
                  v-model="homeCategories"
                  group="categories"
                  :style="{
                    minHeight: `150px`,
                  }"
                >
                  <v-list-item
                    v-for="(item, index) in homeCategories"
                    :key="`${item.name}-${index}`"
                  >
                    <v-list-item-icon>
                      <v-icon>mdi-menu</v-icon>
                    </v-list-item-icon>

                    <v-list-item-content>
                      <v-list-item-title v-text="item.name"></v-list-item-title>
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
                  <v-btn absolute right x-small color="success" icon>
                    <v-icon>mdi-plus</v-icon></v-btn
                  >
                </span>
              </h3>
            </v-card-text>
            <v-divider></v-divider>
            <v-list
              min-height="200"
              dense
              max-height="200"
              style="overflow:auto"
            >
              <v-list-item-group>
                <draggable
                  v-model="categories"
                  group="categories"
                  :style="{
                    minHeight: `150px`,
                  }"
                >
                  <v-list-item
                    v-for="(item, index) in categories"
                    :key="`${item.name}-${index}`"
                  >
                    <v-list-item-icon>
                      <v-icon>mdi-menu</v-icon>
                    </v-list-item-icon>

                    <v-list-item-content>
                      <v-list-item-title v-text="item.name"></v-list-item-title>
                    </v-list-item-content>
                    <v-list-item-icon
                      @click="deleteCategoryfromDatabase(item.slug)"
                    >
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
import api from "@/api";
import draggable from "vuedraggable";

export default {
  components: {
    draggable,
  },
  data() {
    return {
      homeCategories: null,
      showLimit: null,
      showRecent: true,
    };
  },
  mounted() {
    this.getOptions();
  },
  computed: {
    categories() {
      return this.$store.getters.getCategories;
    },
  },
  methods: {
    deleteCategoryfromDatabase(category) {
      api.categories.delete(category);
      this.$store.dispatch("requestHomePageSettings");
    },
    getOptions() {
      this.showLimit = this.$store.getters.getShowLimit;
      this.showRecent = this.$store.getters.getShowRecent;
      this.homeCategories = this.$store.getters.getHomeCategories;
    },
    deleteActiveCategory(index) {
      this.homeCategories.splice(index, 1);
    },
    saveSettings() {
      this.homeCategories.forEach((element, index) => {
        element.position = index + 1;
      });
      this.$store.commit("setShowRecent", this.showRecent);
      this.$store.commit("setShowLimit", this.showLimit);
      this.$store.commit("setHomeCategories", this.homeCategories);
    },
  },
};
</script>

<style>
</style>