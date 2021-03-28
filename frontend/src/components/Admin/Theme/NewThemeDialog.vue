<template>
  <div>
    <v-btn text color="info" @click="dialog = true">
      {{ $t("settings.add-a-new-theme") }}
    </v-btn>
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-app-bar dense dark color="primary mb-2">
          <v-icon large left class="mt-1">
            mdi-format-color-fill
          </v-icon>

          <v-toolbar-title class="headline">
            {{ $t("settings.add-a-new-theme") }}
          </v-toolbar-title>

          <v-spacer></v-spacer>
        </v-app-bar>
        <v-card-title> </v-card-title>
        <v-form @submit.prevent="select">
          <v-card-text>
            <v-text-field
              :label="$t('settings.theme.theme-name')"
              v-model="themeName"
              :rules="[rules.required]"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="dialog = false">
              {{ $t("general.cancel") }}
            </v-btn>
            <v-btn color="success" text type="submit" :disabled="!themeName">
              {{ $t("general.create") }}
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  props: {
    buttonText: String,
    value: String,
  },
  data() {
    return {
      dialog: false,
      themeName: "",
      rules: {
        required: val =>
          !!val || this.$t("settings.theme.theme-name-is-required"),
      },
    };
  },

  watch: {
    color() {
      this.updateColor();
    },
  },
  methods: {
    randomColor() {
      return "#" + Math.floor(Math.random() * 16777215).toString(16);
    },
    select() {
      const newTheme = {
        name: this.themeName,
        colors: {
          primary: "#E58325",
          accent: "#00457A",
          secondary: "#973542",
          success: "#5AB1BB",
          info: "#4990BA",
          warning: "#FF4081",
          error: "#EF5350",
        },
      };

      this.$emit("new-theme", newTheme);
      this.dialog = false;
    },
  },
};
</script>

<style>
</style>