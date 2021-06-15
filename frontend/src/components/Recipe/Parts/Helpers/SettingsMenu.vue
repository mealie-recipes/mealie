<template>
  <div class="text-center">
    <v-menu offset-y top nudge-top="6" :close-on-content-click="false">
      <template v-slot:activator="{ on, attrs }">
        <v-btn color="accent" dark v-bind="attrs" v-on="on">
          <v-icon left>
            mdi-cog
          </v-icon>
          {{ $t("general.settings") }}
        </v-btn>
      </template>
      <v-card>
        <v-card-title class="py-2">
          <div>
            {{ $t("recipe.recipe-settings") }}
          </div>
        </v-card-title>
        <v-divider class="mx-2"></v-divider>
        <v-card-text class="mt-n5">
          <v-switch
            dense
            v-for="(itemValue, key) in value"
            :key="key"
            v-model="value[key]"
            flat
            inset
            :label="labels[key]"
            hide-details
          ></v-switch>
        </v-card-text>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
export default {
  components: {},
  props: {
    value: Object,
  },

  computed: {
    labels() {
      return {
        public: this.$t("recipe.public-recipe"),
        showNutrition: this.$t("recipe.show-nutrition-values"),
        showAssets: this.$t("recipe.show-assets"),
        landscapeView: this.$t("recipe.landscape-view-coming-soon"),
        disableComments: this.$t("recipe.disable-comments"),
        disableAmount: this.$t("recipe.disable-amount"),
      };
    },
  },

  methods: {},
};
</script>

<style lang="scss" scoped></style>
