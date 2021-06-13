<template>
  <v-tooltip bottom nudge-right="50" :color="buttonStyle ? 'primary' : 'secondary'">
    <template v-slot:activator="{ on, attrs }">
      <v-btn
        small
        @click.prevent="toggleFavorite"
        v-if="isFavorite || showAlways"
        :color="buttonStyle ? 'primary' : 'secondary'"
        :icon="!buttonStyle"
        :fab="buttonStyle"
        v-bind="attrs"
        v-on="on"
      >
        <v-icon :small="!buttonStyle" color="secondary">
          {{ isFavorite ? "mdi-heart" : "mdi-heart-outline" }}
        </v-icon>
      </v-btn>
    </template>
    <span>{{ isFavorite ? $t("recipe.remove-from-favorites") : $t("recipe.add-to-favorites") }}</span>
  </v-tooltip>
</template>

<script>
import { api } from "@/api";
export default {
  props: {
    slug: {
      default: "",
    },
    showAlways: {
      type: Boolean,
      default: false,
    },
    buttonStyle: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    user() {
      return this.$store.getters.getUserData;
    },
    isFavorite() {
      return this.user.favoriteRecipes.indexOf(this.slug) !== -1;
    },
  },
  methods: {
    async toggleFavorite() {
      if (!this.isFavorite) {
        await api.users.addFavorite(this.user.id, this.slug);
      } else {
        await api.users.removeFavorite(this.user.id, this.slug);
      }
      this.$store.dispatch("requestUserData");
    },
  },
};
</script>

<style lang="scss" scoped>
</style>