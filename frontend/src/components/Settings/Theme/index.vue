<template>
  <v-card>
    <v-card-title class="headline">
      {{ $t("settings.theme.theme-settings") }}
    </v-card-title>
    <v-divider></v-divider>
    <v-card-text>
      <h2 class="mt-4 mb-1">{{ $t("settings.theme.dark-mode") }}</h2>
      <p>
        {{
          $t(
            "settings.theme.choose-how-mealie-looks-to-you-set-your-theme-preference-to-follow-your-system-settings-or-choose-to-use-the-light-or-dark-theme"
          )
        }}
      </p>
      <v-row dense align="center">
        <v-col cols="12">
          <v-btn-toggle
            v-model="selectedDarkMode"
            color="primary "
            mandatory
            @change="setStoresDarkMode"
          >
            <v-btn value="system">
              {{ $t("settings.theme.default-to-system") }}
            </v-btn>

            <v-btn value="light"> {{ $t("settings.theme.light") }} </v-btn>

            <v-btn value="dark"> {{ $t("settings.theme.dark") }} </v-btn>
          </v-btn-toggle>
        </v-col>
      </v-row></v-card-text
    >
    <v-divider></v-divider>
    <v-card-text>
      <h2 class="mt-1 mb-1">{{ $t("settings.theme.theme") }}</h2>
      <p>
        {{
          $t(
            "settings.theme.select-a-theme-from-the-dropdown-or-create-a-new-theme-note-that-the-default-theme-will-be-served-to-all-users-who-have-not-set-a-theme-preference"
          )
        }}
      </p>

      <v-form ref="form" lazy-validation>
        <v-row dense align="center">
          <v-col md="4" sm="3">
            <v-select
              :label="$t('settings.theme.saved-color-theme')"
              :items="availableThemes"
              item-text="name"
              return-object
              v-model="selectedTheme"
              @change="themeSelected"
              :rules="[(v) => !!v || $t('settings.theme.theme-is-required')]"
              required
            >
            </v-select>
          </v-col>
          <v-col>
            <v-btn-toggle group class="mt-n5">
              <NewThemeDialog @new-theme="appendTheme" class="mt-1" />
              <v-btn text color="error" @click="deleteSelectedThemeValidation">
                {{ $t("general.delete") }}
              </v-btn>
            </v-btn-toggle>
            <Confirmation
              :title="$t('settings.theme.delete-theme')"
              :message="
                $t('settings.theme.are-you-sure-you-want-to-delete-this-theme')
              "
              color="error"
              icon="mdi-alert-circle"
              ref="deleteThemeConfirm"
              v-on:confirm="deleteSelectedTheme()"
            />
          </v-col>
          <v-spacer></v-spacer>
        </v-row>
      </v-form>
      <v-row dense align-content="center" v-if="selectedTheme.colors">
        <v-col>
          <ColorPickerDialog
            :button-text="$t('settings.theme.primary')"
            v-model="selectedTheme.colors.primary"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog
            :button-text="$t('settings.theme.secondary')"
            v-model="selectedTheme.colors.secondary"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog
            :button-text="$t('settings.theme.accent')"
            v-model="selectedTheme.colors.accent"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog
            :button-text="$t('settings.theme.success')"
            v-model="selectedTheme.colors.success"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog
            :button-text="$t('settings.theme.info')"
            v-model="selectedTheme.colors.info"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog
            :button-text="$t('settings.theme.warning')"
            v-model="selectedTheme.colors.warning"
          />
        </v-col>
        <v-col>
          <ColorPickerDialog
            :button-text="$t('settings.theme.error')"
            v-model="selectedTheme.colors.error"
          />
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="success" @click="saveThemes" class="mr-2">
        <v-icon left> mdi-content-save </v-icon>
        {{ $t("general.save") }}
      </v-btn>
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

