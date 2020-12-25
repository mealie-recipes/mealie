<template>
  <div class="text-center">
    <v-dialog v-model="addRecipe" width="650" @click:outside="reset">
      <v-card :loading="processing">
        <v-card-title class="headline"> From URL </v-card-title>

        <v-card-text>
          <v-form>
            <v-text-field v-model="recipeURL" label="Recipe URL"></v-text-field>
          </v-form>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="createRecipe"> Submit </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-speed-dial v-model="fab" fixed right bottom open-on-hover>
      <template v-slot:activator>
        <v-btn v-model="fab" color="secondary" dark fab @click="navCreate">
          <v-icon> mdi-plus </v-icon>
        </v-btn>
      </template>
      <v-btn fab dark small color="success" @click="addRecipe = true">
        <v-icon>mdi-link</v-icon>
      </v-btn>
    </v-speed-dial>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return {
      fab: false,
      addRecipe: false,
      recipeURL: "",
      processing: false,
    };
  },

  methods: {
    async createRecipe() {
      this.processing = true;
      await api.recipes.createByURL(this.recipeURL);
      this.addRecipe = false;
      this.processing = false;
    },

    navCreate() {
      this.$router.push("/new");
    },

    reset() {
      (this.fab = false),
        (this.addRecipe = false),
        (this.recipeURL = ""),
        (this.processing = false);
    },
  },
};
</script>

<style>
</style>