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
            v-model="selectedDarkMode"
            color="primary "
            mandatory
            @change="setStoresDarkMode"
          >
            <v-btn value="system"> Default to system </v-btn>

            <v-btn value="light"> Light </v-btn>

            <v-btn value="dark"> Dark </v-btn>
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
              v-model="selectedTheme"
              @change="themeSelected"
              :rules="[(v) => !!v || 'Theme is required']"
              required
            >
            </v-select>
          </v-col>
          <v-col cols="12" sm="1">
            <NewThemeDialog @new-theme="appendTheme" />
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
      <v-row dense align-content="center" v-if="selectedTheme.colors">
        <v-col>
          <ColorPickerDialog
            button-text="Primary"
            v-model="selectedTheme.colors.primary"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog
            button-text="Secondary"
            v-model="selectedTheme.colors.secondary"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog
            button-text="Accent"
            v-model="selectedTheme.colors.accent"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog
            button-text="Success"
            v-model="selectedTheme.colors.success"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog button-text="Info" v-model="selectedTheme.colors.info" />
        </v-col>
        <v-col>
          <ColorPickerDialog
            button-text="Warning"
            v-model="selectedTheme.colors.warning"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog
            button-text="Error"
            v-model="selectedTheme.colors.error"
          />
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-actions>
      <v-row>
        <v-col> </v-col>
        <v-col></v-col>
        <v-col align="end">
          <v-btn text color="success" @click="saveThemes">
            Save Colors and Apply Theme
          </v-btn>
        </v-col>
      </v-row>
    </v-card-actions>
  </v-card>
</template>

<script>
import api from "../../../api";
import ColorPickerDialog from "./ColorPickerDialog";
import NewThemeDialog from "./NewThemeDialog";
import Confirmation from "../../UI/Confirmation";

export default {
  components: {
    ColorPickerDialog,
    Confirmation,
    NewThemeDialog,
  },
  data() {
    return {
      selectedTheme: {},
      selectedDarkMode: "system",
      availableThemes: [],
    };
  },
  async mounted() {
    this.availableThemes = await api.themes.requestAll();
    this.selectedTheme = this.$store.getters.getActiveTheme;
    this.selectedDarkMode = this.$store.getters.getDarkMode;
    console.log(this.selectedDarkMode);
  },

  methods: {
    /**
     * Open the delete confirmation.
     */
    deleteSelectedThemeValidation() {
      if (this.$refs.form.validate()) {
        if (this.selectedTheme.name === "default") {
          // Notify User Can't Delete Default
        } else if (this.selectedTheme !== {}) {
          this.$refs.deleteThemeConfirm.open();
        }
      }
    },
    /**
     * Delete the selected Theme
     */
    async deleteSelectedTheme() {
      //Delete Theme from DB
      await api.themes.delete(this.selectedTheme.name);

      //Get the new list of available from DB
      this.availableThemes = await api.themes.requestAll();

      //Change to default if deleting current theme.
      if (
        !this.availableThemes.some(
          (theme) => theme.name === this.selectedTheme.name
        )
      ) {
        await this.$store.dispatch("resetTheme");
        this.selectedTheme = this.$store.getters.getActiveTheme;
      }
    },
    /**
     * Create the new Theme and select it.
     */
    async appendTheme(NewThemeDialog) {
      await api.themes.create(NewThemeDialog);
      this.availableThemes.push(NewThemeDialog);
      this.selectedTheme = NewThemeDialog;
    },

    themeSelected() {
      //TODO Revamp Theme selection.
      //console.log("this.activeTheme", this.selectedTheme);
    },

    setStoresDarkMode() {
      console.log(this.selectedDarkMode);
      this.$store.commit("setDarkMode", this.selectedDarkMode);
    },
    /**
     * This will save the current colors and make the selected theme live.
     */
    async saveThemes() {
      if (this.$refs.form.validate()) {
        this.$store.commit("setTheme", this.selectedTheme);
        await api.themes.update(
          this.selectedTheme.name,
          this.selectedTheme.colors
        );
      }
    },
  },
};
</script>

<style>
</style>

