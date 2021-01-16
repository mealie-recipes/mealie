<template>
  <v-row justify="center">
    <v-dialog v-model="dialog" persistent max-width="800">
      <v-card>
        <v-card-title class="headline"> {{$t('meal-plan.choose-a-recipe')}} </v-card-title>
        <v-card-text>
          <v-autocomplete
            :items="availableRecipes"
            v-model="selected"
            clearable
            return
            dense
            hide-details
            hide-selected
            item-text="slug"
            :label="$t('search.search-for-a-recipe')"
            single-line
          >
            <template v-slot:no-data>
              <v-list-item>
                <v-list-item-title :v-html="$t('search.search-for-your-favorite-recipe')">
                </v-list-item-title>
              </v-list-item>
            </template>
            <template v-slot:item="{ item }">
              <v-row align="center" @click="dialog = false">
                <v-col sm="2">
                  <v-img
                    max-height="100"
                    max-width="100"
                    :src="getImage(item.image)"
                  ></v-img>
                </v-col>
                <v-col sm="10">
                  <h3>
                    {{ item.name }}
                  </h3>
                </v-col>
              </v-row>
            </template>
          </v-autocomplete>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" text @click="dialog = false"> {{$t('general.close')}} </v-btn>
          <v-btn color="secondary" text @click="dialog = false"> {{$t('general.select')}} </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import utils from "../../utils";
export default {
  props: {
    forceDialog: Boolean,
  },

  data() {
    return {
      dialog: false,
      selected: "",
    };
  },

  watch: {
    forceDialog() {
      this.dialog = this.forceDialog;
    },
    selected() {
      if (this.selected) {
        this.$emit("select", this.selected);
      }
    },
    dialog() {
      if (this.dialog === false) {
        this.$emit("close");
      } else {
        this.selected = "";
      }
    },
  },

  computed: {
    availableRecipes() {
      return this.$store.getters.getRecentRecipes;
    },
  },

  methods: {
    getImage(slug) {
      return utils.getImageURL(slug);
    },
  },
};
</script>

<style>
</style>