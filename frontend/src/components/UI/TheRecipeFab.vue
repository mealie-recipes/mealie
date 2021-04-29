<template>
  <div class="text-center">
    <v-dialog v-model="addRecipe" width="650" @click:outside="reset">
      <v-card :loading="processing">
        <v-app-bar dark color="primary mb-2">
          <v-icon large left v-if="!processing">
            mdi-link
          </v-icon>
          <v-progress-circular
            v-else
            indeterminate
            color="white"
            large
            class="mr-2"
          >
          </v-progress-circular>

          <v-toolbar-title class="headline">
            {{ $t("new-recipe.from-url") }}
          </v-toolbar-title>

          <v-spacer></v-spacer>
        </v-app-bar>
        <v-form ref="urlForm" @submit.prevent="createRecipe">
          <v-card-text>
            <v-text-field
              v-model="recipeURL"
              :label="$t('new-recipe.recipe-url')"
              required
              validate-on-blur
              autofocus
              class="mt-1"
              :rules="[isValidWebUrl]"
              :hint="$t('new-recipe.url-form-hint')"
              persistent-hint
            ></v-text-field>

            <v-alert v-if="error" color="red" outlined type="success">
              {{ $t("new-recipe.error-message") }}
            </v-alert>
          </v-card-text>

          <v-divider></v-divider>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="reset">
              {{ $t("general.close") }}
            </v-btn>
            <v-btn color="success" text type="submit" :loading="processing">
              {{ $t("general.submit") }}
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
    <v-speed-dial
      v-model="fab"
      :open-on-hover="absolute"
      :fixed="absolute"
      :bottom="absolute"
      :right="absolute"
    >
      <template v-slot:activator>
        <v-btn
          v-model="fab"
          :color="absolute ? 'accent' : 'white'"
          dark
          :icon="!absolute"
          :fab="absolute"
        >
          <v-icon> mdi-plus </v-icon>
        </v-btn>
      </template>
      <v-btn fab dark small color="primary" @click="addRecipe = true">
        <v-icon>mdi-link</v-icon>
      </v-btn>
      <v-btn fab dark small color="accent" @click="$router.push('/new')">
        <v-icon>mdi-square-edit-outline</v-icon>
      </v-btn>
    </v-speed-dial>
  </div>
</template>

<script>
import { api } from "@/api";

export default {
  props: {
    absolute: {
      default: false,
    },
  },
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
      if (this.$refs.urlForm.validate()) {
        this.processing = true;
        const response = await api.recipes.createByURL(this.recipeURL);
        this.processing = false;
        if (response) {
          this.addRecipe = false;
          this.recipeURL = "";
          this.$router.push(`/recipe/${response.data}`);
        } else {
          this.error = true;
        }
      }
    },

    reset() {
      this.fab = false;
      this.error = false;
      this.addRecipe = false;
      this.recipeURL = "";
      this.processing = false;
    },
    isValidWebUrl(url) {
      let regEx = /^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$/gm;
      return regEx.test(url) ? true : "Must be a Valid URL";
    },
  },
};
</script>

<style>
</style>