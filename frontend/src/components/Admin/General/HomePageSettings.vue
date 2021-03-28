<template>
  <v-card flat>
    <v-card-text>
      <h2 class="mt-1 mb-1">{{ $t("settings.homepage.home-page") }}</h2>
      <v-row align="center" justify="center" dense class="mb-n7 pb-n5">
        <v-col cols="1">
          <LanguageMenu @select-lang="writeLang" :site-settings="true" />
        </v-col>
        <v-col cols="12" sm="3" md="2">
          <v-switch
            v-model="settings.showRecent"
            :label="$t('settings.homepage.show-recent')"
          ></v-switch>
        </v-col>
        <v-col cols="12" sm="5" md="5">
          <v-slider
            class="pt-sm-4"
            :label="$t('settings.homepage.card-per-section')"
            v-model="settings.cardsPerSection"
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
        <v-col cols="12" sm="6">
          <v-card outlined min-height="350px">
            <v-app-bar dark dense color="primary">
              <v-icon left>
                mdi-home
              </v-icon>

              <v-toolbar-title class="headline">
                {{ $t("settings.homepage.home-page-sections") }}
              </v-toolbar-title>

              <v-spacer></v-spacer>
            </v-app-bar>
            <v-list height="300" dense style="overflow:auto">
              <v-list-item-group>
                <draggable
                  v-model="settings.categories"
                  group="categories"
                  :style="{
                    minHeight: `150px`,
                  }"
                >
                  <v-list-item
                    v-for="(item, index) in settings.categories"
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
        <v-col cols="12" sm="6">
          <v-card outlined height="350px">
            <v-app-bar dark dense color="primary">
              <v-icon left>
                mdi-tag
              </v-icon>

              <v-toolbar-title class="headline">
                {{ $t("settings.homepage.all-categories") }}
              </v-toolbar-title>

              <v-spacer></v-spacer>
            </v-app-bar>
            <v-list height="300" dense style="overflow:auto">
              <v-list-item-group>
                <draggable
                  v-model="allCategories"
                  group="categories"
                  :style="{
                    minHeight: `150px`,
                  }"
                >
                  <v-list-item
                    v-for="(item, index) in allCategories"
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
import LanguageMenu from "@/components/UI/LanguageMenu";
import draggable from "vuedraggable";

export default {
  components: {
    draggable,
    LanguageMenu,
  },
  data() {
    return {
      settings: {
        language: "en",
        showRecent: null,
        cardsPerSection: null,
        categories: [],
      },
    };
  },
  mounted() {
    this.getOptions();
  },
  computed: {
    allCategories() {
      return this.$store.getters.getAllCategories;
    },
  },

  methods: {
    writeLang(val) {
      this.settings.language = val;
    },
    deleteCategoryfromDatabase(category) {
      api.categories.delete(category);
    },
    async getOptions() {
      this.settings = await api.siteSettings.get();
    },
    deleteActiveCategory(index) {
      this.settings.categories.splice(index, 1);
    },
    async saveSettings() {
      await api.siteSettings.update(this.settings);
      this.getOptions();
    },
  },
};
</script>

<style>
</style>