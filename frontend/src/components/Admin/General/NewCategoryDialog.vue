<template>
  <div>
    <v-btn icon @click="dialog = true">
      <v-icon color="white">mdi-plus</v-icon>
    </v-btn>
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-app-bar dense dark color="primary mb-2">
          <v-icon large left class="mt-1">
            mdi-tag
          </v-icon>

          <v-toolbar-title class="headline">
            Create a Category
          </v-toolbar-title>

          <v-spacer></v-spacer>
        </v-app-bar>
        <v-card-title> </v-card-title>
        <v-form @submit.prevent="select">
          <v-card-text>
            <v-text-field
              dense
              label="Category Name"
              v-model="categoryName"
              :rules="[rules.required]"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="dialog = false">
              {{ $t("general.cancel") }}
            </v-btn>
            <v-btn color="success" text type="submit" :disabled="!categoryName">
              {{ $t("general.create") }}
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { api } from "@/api";
export default {
  props: {
    buttonText: String,
    value: String,
  },
  data() {
    return {
      dialog: false,
      categoryName: "",
      rules: {
        required: val =>
          !!val || this.$t("settings.theme.theme-name-is-required"),
      },
    };
  },
  watch: {
    dialog(val) {
      if (!val) this.categoryName = "";
    },
  },

  methods: {
    async select() {
      await api.categories.create(this.categoryName);
      this.$emit("new-category", this.categoryName);
      this.dialog = false;
    },
  },
};
</script>

<style>
</style>