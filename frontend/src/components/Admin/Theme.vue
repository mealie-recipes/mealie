<template>
  <v-card>
    <v-card-title class="secondary white--text"> Theme Settings </v-card-title>

    <v-card-text>
      <h2 class="mt-4 mb-1">Dark Mode</h2>
      <p>
        Choose how Mealie looks to you. Set your theme preference to follow your
        system settings, or choose to use the light or dark theme.
      </p>
      <v-row dense align="center">
        <v-col cols="12">
          <v-btn-toggle
            v-model="darkMode"
            color="primary "
            mandatory
            @change="setDarkMode"
          >
            <v-btn value="system">
              Default to system
            </v-btn>

            <v-btn value="light">
              Light
            </v-btn>

            <v-btn value="dark">
              Dark
            </v-btn>
          </v-btn-toggle>
        </v-col>
      </v-row></v-card-text
    >
    <v-divider class=""></v-divider>
    <v-card-text>
      <h2 class="mt-1 mb-1">Theme</h2>
      <p>
        Select a theme from the dropdown or create a new theme. Note that the
        default theme will be served to all users who have not set a theme
        preference.
      </p>

      <v-form ref="form" lazy-validation>
        <v-row dense align="center">
          <v-col cols="12" md="4" sm="3">
            <v-select
              label="Saved Color Theme"
              :items="availableThemes"
              item-text="name"
              return-object
              v-model="activeTheme"
              @change="themeSelected"
              :rules="[v => !!v || 'Theme is required']"
              required
            >
            </v-select>
          </v-col>
          <v-col cols="12" sm="1">
            <NewTheme @new-theme="appendTheme" />
          </v-col>
          <v-col cols="12" sm="1">
            <v-btn text color="error" @click="deleteSelectedThemeValidation">
              Delete
            </v-btn>
            <Confirmation
              title="Delete Theme"
              message="Are you sure you want to delete this theme?"
              color="error"
              icon="mdi-alert-circle"
              ref="deleteThemeConfirm"
              v-on:confirm="deleteSelectedTheme()"
            />
          </v-col>
        </v-row>
      </v-form>
      <v-row dense align-content="center" v-if="activeTheme.colors">
        <v-col>
          <ColorPicker
            button-text="Primary"
            v-model="activeTheme.colors.primary"
          />
        </v-col>
        <v-col>
          <ColorPicker
            button-text="Secondary"
            v-model="activeTheme.colors.secondary"
          />
        </v-col>
        <v-col>
          <ColorPicker
            button-text="Accent"
            v-model="activeTheme.colors.accent"
          />
        </v-col>
        <v-col>
          <ColorPicker
            button-text="Success"
            v-model="activeTheme.colors.success"
          />
        </v-col>
        <v-col>
          <ColorPicker button-text="Info" v-model="activeTheme.colors.info" />
        </v-col>
        <v-col>
          <ColorPicker
            button-text="Warning"
            v-model="activeTheme.colors.warning"
          />
        </v-col>
        <v-col>
          <ColorPicker button-text="Error" v-model="activeTheme.colors.error" />
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-actions>
      <v-row>
        <v-col> </v-col>
        <v-col></v-col>
        <v-col align="end">
          <v-btn text color="success" @click="saveThemes"> Save Theme </v-btn>
        </v-col>
      </v-row>
    </v-card-actions>
  </v-card>
</template>

<script>
import api from "../../api";
import ColorPicker from "./ThemeUI/ColorPicker";
import NewTheme from "./ThemeUI/NewTheme";
import Confirmation from "../UI/Confirmation";

export default {
  components: {
    ColorPicker,
    Confirmation,
    NewTheme
  },
  data() {
    return {
      activeTheme: {},
      darkMode: "system",
      availableThemes: []
    };
  },
  async mounted() {
    this.availableThemes = await api.themes.requestAll();
    this.activeTheme = this.$store.getters.getActiveTheme;
    this.darkMode = this.$store.getters.getDarkMode;
  },

  methods: {
    deleteSelectedThemeValidation() {
      if (this.$refs.form.validate()) {
        if (this.activeTheme.name === "default") {
          // Notify User Can't Delete Default
        } else if (this.activeTheme !== {}) {
          this.$refs.deleteThemeConfirm.open();
        }
      }
    },
    async deleteSelectedTheme() {
      api.themes.delete(this.activeTheme.name);
      this.availableThemes = await api.themes.requestAll();
      //Change to default if deleting current theme.

      if (
        !this.availableThemes.some(
          theme => theme.name === this.activeTheme.name
        )
      ) {
        this.$store.commit("setActiveTheme", null);
        this.activeTheme = this.$store.getters.getActiveTheme;
      }
    },
    async appendTheme(newTheme) {
      api.themes.create(newTheme);
      this.availableThemes.push(newTheme);
      this.activeTheme = newTheme;
    },
    themeSelected() {
      console.log("this.activeTheme", this.activeTheme);
    },

    setDarkMode() {
      this.$store.commit("setDarkMode", this.darkMode);
    },
    /**
     * This will save the current colors and make the selected theme live.
     */
    async saveThemes() {
      if (this.$refs.form.validate()) {
        this.$store.commit("setActiveTheme", this.activeTheme);
        this.$store.dispatch("initCookies");
        api.themes.update(this.activeTheme.name, this.activeTheme);
      } else;
    }
  }
};
</script>

<style>
</style>

