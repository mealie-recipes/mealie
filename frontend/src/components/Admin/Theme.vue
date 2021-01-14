<template>
  <v-card>
    <v-card-title class="secondary white--text"> {{$t('settings.theme.theme-settings')}} </v-card-title>
    <v-card-text>
      <p>
        {{$t('settings.theme.select-a-theme-from-the-dropdown-or-create-a-new-theme-note-that-the-default-theme-will-be-served-to-all-users-who-have-not-set-a-theme-preference')}}
      </p>
      <v-row dense align="center">
        <v-col cols="12" md="2" sm="5">
          <v-switch
            v-model="darkMode"
            inset
            :label="$t('settings.theme.dark-mode')"
            class="my-n3"
            @change="toggleDarkMode"
          ></v-switch>
        </v-col>
        <v-col cols="12" md="4" sm="3">
          <v-form ref="form" lazy-validation>
            <v-select
              :label="$t('settings.theme.saved-color-schemes')"
              :items="availableThemes"
              item-text="name"
              item-value="colors"
              return-object
              v-model="selectedScheme"
              @change="themeSelected"
              :rules="[(v) => !!v || $t('settings.theme.theme-is-required')]"
              required
            >
            </v-select>
          </v-form>
        </v-col>
        <v-col cols="12" sm="1">
          <NewTheme @new-theme="appendTheme" />
        </v-col>
        <v-col cols="12" sm="1">
          <v-btn text color="error" @click="deleteSelected"> {{$t('general.delete')}} </v-btn>
        </v-col>
      </v-row>
      <v-row dense align-content="center" v-if="activeTheme">
        <v-col>
          <ColorPicker :button-text="$t('settings.theme.primary')" v-model="activeTheme.primary" />
        </v-col>
        <v-col>
          <ColorPicker
            :button-text="$t('settings.theme.secondary')"
            v-model="activeTheme.secondary"
          />
        </v-col>
        <v-col>
          <ColorPicker :button-text="$t('settings.theme.accent')" v-model="activeTheme.accent" />
        </v-col>
        <v-col>
          <ColorPicker :button-text="$t('settings.theme.success')" v-model="activeTheme.success" />
        </v-col>
        <v-col>
          <ColorPicker :button-text="$t('settings.theme.info')" v-model="activeTheme.info" />
        </v-col>
        <v-col>
          <ColorPicker :button-text="$t('settings.theme.warning')" v-model="activeTheme.warning" />
        </v-col>
        <v-col>
          <ColorPicker :button-text="$t('settings.theme.error')" v-model="activeTheme.error" />
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-actions>
      <v-row>
        <v-col> </v-col>
        <v-col></v-col>
        <v-col align="end">
          <v-btn text color="success" @click="saveThemes"> {{$t('settings.theme.save-theme')}} </v-btn>
        </v-col>
      </v-row>
    </v-card-actions>
  </v-card>
</template>

<script>
import api from "../../api";
import ColorPicker from "./ThemeUI/ColorPicker";
import NewTheme from "./ThemeUI/NewTheme";

export default {
  components: {
    ColorPicker,
    NewTheme,
  },
  data() {
    return {
      themes: null,
      activeTheme: {},
      darkMode: false,
      availableThemes: [],
      selectedScheme: "",
      selectedLight: "",
    };
  },
  async mounted() {
    this.availableThemes = await api.themes.requestAll();
    this.darkMode = this.$store.getters.getDarkMode;
    this.themes = this.$store.getters.getThemes;
    this.setThemeEditor();
  },

  methods: {
    async deleteSelected() {
      if (this.$refs.form.validate()) {
        if (this.selectedScheme === "default") {
          // Notify User Can't Delete Default
        } else if (this.selectedScheme !== "") {
          api.themes.delete(this.selectedScheme.name);
        }
        this.availableThemes = await api.themes.requestAll();
      }
    },
    async appendTheme(newTheme) {
      api.themes.create(newTheme);
      this.availableThemes.push(newTheme);
    },
    themeSelected() {
      this.activeTheme = this.selectedScheme.colors;
    },
    setThemeEditor() {
      if (this.darkMode) {
        this.activeTheme = this.themes.dark;
      } else {
        this.activeTheme = this.themes.light;
      }
    },
    toggleDarkMode() {
      this.$store.commit("setDarkMode", this.darkMode);
      this.selectedScheme = "";

      this.setThemeEditor();
    },
    saveThemes() {
      if (this.$refs.form.validate()) {
        if (this.darkMode) {
          this.themes.dark = this.activeTheme;
        } else {
          this.themes.light = this.activeTheme;
        }
        this.$store.commit("setThemes", this.themes);
        this.$store.dispatch("initCookies");
        api.themes.update(this.selectedScheme.name, this.activeTheme);
      } else;
    },
  },
};
</script>

<style>
</style>

