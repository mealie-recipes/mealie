<template>
  <div class="text-center">
    <v-dialog v-model="addRecipe" width="650" @click:outside="reset">
      <v-card :loading="processing">
        <v-card-title class="headline">{{ $t('new-recipe.from-url') }} </v-card-title>

        <v-card-text>
          <v-form>
            <v-text-field v-model="recipeURL" :label="$t('new-recipe.recipe-url')"></v-text-field>
          </v-form>

          <v-alert v-if="error" color="red" outlined type="success">
            {{ $t('new-recipe.error-message') }}
          </v-alert>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="createRecipe"> {{ $t('general.submit') }} </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-speed-dial v-model="fab" fixed right bottom open-on-hover>
      <template v-slot:activator>
        <v-btn v-model="fab" color="accent" dark fab @click="navCreate">
          <v-icon> mdi-plus </v-icon>
        </v-btn>
      </template>
      <v-btn fab dark small color="primary" @click="addRecipe = true">
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
      error: false,
      fab: false,
      addRecipe: false,
      recipeURL: "",
      processing: false,
    };
  },

  methods: {
    async createRecipe() {
      this.processing = true;
      let response = await api.recipes.createByURL(this.recipeURL);
      if (response.status !== 201) {
        this.error = true;
        this.processing = false;
        return;
      }

      this.addRecipe = false;
      this.processing = false;
      this.$router.push(`/recipe/${response.data}`);
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