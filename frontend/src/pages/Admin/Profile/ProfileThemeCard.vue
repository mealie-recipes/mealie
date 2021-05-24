<template>
  <div>
    <StatCard icon="mdi-format-color-fill" :color="color">
      <template v-slot:after-heading>
        <div class="ml-auto text-right">
          <div class="body-3 grey--text font-weight-light" v-text="$t('general.themes')" />

          <h3 class="display-2 font-weight-light text--primary">
            <small> {{ selectedTheme.name }} </small>
          </h3>
        </div>
      </template>

      <template v-slot:actions>
        <v-btn-toggle v-model="darkMode" color="primary " mandatory>
          <v-btn small value="system">
            <v-icon>mdi-desktop-tower-monitor</v-icon>
            <span class="ml-1" v-show="$vuetify.breakpoint.smAndUp">
              {{ $t("settings.theme.default-to-system") }}
            </span>
          </v-btn>

          <v-btn small value="light">
            <v-icon>mdi-white-balance-sunny</v-icon>
            <span class="ml-1" v-show="$vuetify.breakpoint.smAndUp">
              {{ $t("settings.theme.light") }}
            </span>
          </v-btn>

          <v-btn small value="dark">
            <v-icon>mdi-weather-night</v-icon>
            <span class="ml-1" v-show="$vuetify.breakpoint.smAndUp">
              {{ $t("settings.theme.dark") }}
            </span>
          </v-btn>
        </v-btn-toggle>
      </template>

      <template v-slot:bottom>
        <v-virtual-scroll height="290" item-height="70" :items="availableThemes" class="mt-2">
          <template v-slot:default="{ item }">
            <v-divider></v-divider>
            <v-list-item @click="selectedTheme = item">
              <v-list-item-avatar>
                <v-icon large dark :color="item.colors.primary">
                  mdi-format-color-fill
                </v-icon>
              </v-list-item-avatar>

              <v-list-item-content>
                <v-list-item-title v-text="item.name"></v-list-item-title>

                <v-row flex align-center class="mt-2 justify-space-around px-4 pb-2">
                  <v-sheet
                    class="rounded flex mx-1"
                    v-for="(item, index) in item.colors"
                    :key="index"
                    :color="item"
                    height="20"
                  >
                  </v-sheet>
                </v-row>
              </v-list-item-content>

              <v-list-item-action class="ml-auto">
                <v-btn large icon @click.stop="editTheme(item)">
                  <v-icon color="accent">{{ $globals.icons.edit }}</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
            <v-divider></v-divider>
          </template>
        </v-virtual-scroll>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <TheButton class="mt-1 mb-n1" create @click="createTheme" />
        </v-card-actions>
      </template>
    </StatCard>
    <BaseDialog
      :loading="loading"
      :title="modalLabel.title"
      title-icon="mdi-format-color-fill"
      modal-width="700"
      ref="themeDialog"
      :submit-text="modalLabel.button"
      @submit="processSubmit"
      @delete="deleteTheme"
    >
      <v-card-text class="mt-3">
        <v-text-field
          :label="$t('settings.theme.theme-name')"
          v-model="defaultData.name"
          :rules="[rules.required]"
          :append-outer-icon="jsonEditor ? 'mdi-form-select' : 'mdi-code-braces'"
          @click:append-outer="jsonEditor = !jsonEditor"
        ></v-text-field>
        <v-row dense dflex wrap justify-content-center v-if="defaultData.colors && !jsonEditor">
          <v-col cols="12" sm="6" v-for="(_, key) in defaultData.colors" :key="key">
            <ColorPickerDialog :button-text="labels[key]" v-model="defaultData.colors[key]" />
          </v-col>
        </v-row>
        <VJsoneditor @error="logError()" v-else v-model="defaultData" height="250px" :options="jsonEditorOptions" />
      </v-card-text>
    </BaseDialog>
  </div>
</template>

<script>
import VJsoneditor from "v-jsoneditor";
import { api } from "@/api";
import ColorPickerDialog from "@/components/FormHelpers/ColorPickerDialog";
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import StatCard from "@/components/UI/StatCard";
export default {
  components: { StatCard, BaseDialog, ColorPickerDialog, VJsoneditor },
  data() {
    return {
      jsonEditor: false,
      jsonEditorOptions: {
        mode: "code",
        search: false,
        mainMenuBar: false,
      },
      availableThemes: [],
      color: "accent",
      newTheme: false,
      loading: false,
      defaultData: {
        name: "",
        colors: {
          primary: "#E58325",
          accent: "#00457A",
          secondary: "#973542",
          success: "#43A047",
          info: "#4990BA",
          warning: "#FF4081",
          error: "#EF5350",
        },
      },
      rules: {
        required: val => !!val || this.$t("settings.theme.theme-name-is-required"),
      },
    };
  },
  computed: {
    labels() {
      return {
        primary: this.$t("settings.theme.primary"),
        secondary: this.$t("settings.theme.secondary"),
        accent: this.$t("settings.theme.accent"),
        success: this.$t("settings.theme.success"),
        info: this.$t("settings.theme.info"),
        warning: this.$t("settings.theme.warning"),
        error: this.$t("settings.theme.error"),
      };
    },
    modalLabel() {
      if (this.newTheme) {
        return {
          title: this.$t("settings.add-a-new-theme"),
          button: this.$t("general.create"),
        };
      } else {
        return {
          title: "Update Theme",
          button: this.$t("general.update"),
        };
      }
    },
    selectedTheme: {
      set(val) {
        this.$store.commit("setTheme", val);
      },
      get() {
        return this.$store.getters.getActiveTheme;
      },
    },
    darkMode: {
      set(val) {
        this.$store.commit("setDarkMode", val);
      },
      get() {
        return this.$store.getters.getDarkMode;
      },
    },
  },
  async mounted() {
    await this.getAllThemes();
  },
  methods: {
    async getAllThemes() {
      this.availableThemes = await api.themes.requestAll();
    },
    editTheme(theme) {
      this.defaultData = theme;
      this.newTheme = false;
      this.$refs.themeDialog.open();
    },
    createTheme() {
      this.newTheme = true;
      this.$refs.themeDialog.open();
    },
    async processSubmit() {
      if (this.newTheme) {
        await api.themes.create(this.defaultData);
      } else {
        await api.themes.update(this.defaultData);
      }
      this.getAllThemes();
    },
    async deleteTheme() {
      await api.themes.delete(this.defaultData.id);
      this.getAllThemes();
    },
  },
};
</script>

<style lang="scss" scoped>
</style>