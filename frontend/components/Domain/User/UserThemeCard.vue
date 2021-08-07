<template>
  <div>
    <BaseStatCard :icon="$globals.icons.formatColorFill" :color="color">
      <template #after-heading>
        <div class="ml-auto text-right">
          <div class="body-3 grey--text font-weight-light" v-text="$t('general.themes')" />

          <h3 class="display-2 font-weight-light text--primary">
            <small> {{ selectedTheme.name }} </small>
          </h3>
        </div>
      </template>

      <template #actions>
        <v-btn-toggle v-model="darkMode" color="primary " mandatory>
          <v-btn small value="system">
            <v-icon>{{ $globals.icons.desktopTowerMonitor }}</v-icon>
            <span v-show="$vuetify.breakpoint.smAndUp" class="ml-1">
              {{ $t("settings.theme.default-to-system") }}
            </span>
          </v-btn>

          <v-btn small value="light">
            <v-icon>{{ $globals.icons.weatherSunny }}</v-icon>
            <span v-show="$vuetify.breakpoint.smAndUp" class="ml-1">
              {{ $t("settings.theme.light") }}
            </span>
          </v-btn>

          <v-btn small value="dark">
            <v-icon>{{ $globals.icons.weatherNight }}</v-icon>
            <span v-show="$vuetify.breakpoint.smAndUp" class="ml-1">
              {{ $t("settings.theme.dark") }}
            </span>
          </v-btn>
        </v-btn-toggle>
      </template>

      <template #bottom>
        <v-virtual-scroll height="290" item-height="70" :items="availableThemes" class="mt-2">
          <template #default="{ item }">
            <v-divider></v-divider>
            <v-list-item @click="selectedTheme = item">
              <v-list-item-avatar>
                <v-icon large dark :color="item.colors.primary">
                  {{ $globals.icons.formatColorFill }}
                </v-icon>
              </v-list-item-avatar>

              <v-list-item-content>
                <v-list-item-title v-text="item.name"></v-list-item-title>

                <v-row flex align-center class="mt-2 justify-space-around px-4 pb-2">
                  <v-sheet
                    v-for="(clr, index) in item.colors"
                    :key="index"
                    class="rounded flex mx-1"
                    :color="clr"
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
          <BaseButton class="ml-auto mt-1 mb-n1" create @click="createTheme" />
        </v-card-actions>
      </template>
    </BaseStatCard>
    <BaseDialog
      ref="themeDialog"
      :loading="loading"
      :title="modalLabel.title"
      :title-icon="$globals.icons.formatColorFill"
      modal-width="700"
      :submit-text="modalLabel.button"
      @submit="processSubmit"
      @delete="deleteTheme"
    >
      <v-card-text class="mt-3">
        <v-text-field
          v-model="defaultData.name"
          :label="$t('settings.theme.theme-name')"
          :append-outer-icon="jsonEditor ? $globals.icons.formSelect : $globals.icons.codeBraces"
          @click:append-outer="jsonEditor = !jsonEditor"
        ></v-text-field>
        <v-row v-if="defaultData.colors && !jsonEditor" dense dflex wrap justify-content-center>
          <v-col v-for="(_, key) in defaultData.colors" :key="key" cols="12" sm="6">
            <BaseColorPicker v-model="defaultData.colors[key]" :button-text="labels[key]" />
          </v-col>
        </v-row>
        <!-- <VJsoneditor v-else v-model="defaultData" height="250px" :options="jsonEditorOptions" @error="logError()" /> -->
      </v-card-text>
    </BaseDialog>
  </div>
</template>

<script>
export default {
  components: {
    // VJsoneditor: () => import(/* webpackChunkName: "json-editor" */ "v-jsoneditor"),
  },
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
        console.log(val);
      },
      get() {
        return this.$vuetify.theme;
      },
    },
    darkMode: {
      set(val) {
        console.log(val);
      },
      get() {
        return false;
      },
    },
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