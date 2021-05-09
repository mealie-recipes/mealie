<template>
  <div>
    <BaseDialog
      :title="$t('settings.backup.create-heading')"
      titleIcon="mdi-database"
      @submit="createBackup"
      :submit-text="$t('general.create')"
      :loading="loading"
    >
      <template v-slot:open="{ open }">
        <v-btn @click="open" class="mx-2" small :color="color">
          <v-icon left> mdi-plus </v-icon> {{ $t("general.custom") }}
        </v-btn>
      </template>
      <v-card-text class="mt-6">
        <v-text-field dense :label="$t('settings.backup.backup-tag')" v-model="tag"></v-text-field>
      </v-card-text>
      <v-card-actions class="mt-n9 flex-wrap">
        <v-switch v-model="fullBackup" :label="switchLabel"></v-switch>
        <v-spacer></v-spacer>
      </v-card-actions>
      <v-expand-transition>
        <div v-if="!fullBackup">
          <v-card-text class="mt-n4">
            <v-row>
              <v-col sm="4">
                <p>{{ $t("general.options") }}</p>
                <ImportOptions @update-options="updateOptions" class="mt-5" />
              </v-col>
              <v-col>
                <p>{{ $t("general.templates") }}</p>
                <v-checkbox
                  v-for="template in availableTemplates"
                  :key="template"
                  class="mb-n4 mt-n3"
                  dense
                  :label="template"
                  @click="appendTemplate(template)"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-card-text>
        </div>
      </v-expand-transition>
    </BaseDialog>
  </div>
</template>

<script>
import BaseDialog from "./BaseDialog";
import ImportOptions from "@/components/FormHelpers/ImportOptions";
import { api } from "@/api";
export default {
  props: {
    color: { default: "primary" },
  },
  components: {
    BaseDialog,
    ImportOptions,
  },
  data() {
    return {
      tag: null,
      fullBackup: true,
      loading: false,
      options: {
        recipes: true,
        settings: true,
        themes: true,
        pages: true,
        users: true,
        groups: true,
      },
      availableTemplates: [],
      selectedTemplates: [],
    };
  },
  computed: {
    switchLabel() {
      if (this.fullBackup) {
        return this.$t("settings.backup.full-backup");
      } else return this.$t("settings.backup.partial-backup");
    },
  },
  mounted() {
    this.resetData();
    this.getAvailableBackups();
  },
  methods: {
    resetData() {
      this.tag = null;
      this.fullBackup = true;
      this.loading = false;
      this.options = {
        recipes: true,
        settings: true,
        themes: true,
        pages: true,
        users: true,
        groups: true,
      };
      this.availableTemplates = [];
      this.selectedTemplates = [];
    },
    updateOptions(options) {
      this.options = options;
    },
    async getAvailableBackups() {
      const response = await api.backups.requestAvailable();
      response.templates.forEach(element => {
        this.availableTemplates.push(element);
      });
    },
    async createBackup() {
      this.loading = true;
      const data = {
        tag: this.tag,
        options: {
          recipes: this.options.recipes,
          settings: this.options.settings,
          pages: this.options.pages,
          themes: this.options.themes,
          users: this.options.users,
          groups: this.options.groups,
        },
        templates: this.selectedTemplates,
      };

      if (await api.backups.create(data)) {
        this.$emit("created");
      }
      this.loading = false;
    },
    appendTemplate(templateName) {
      if (this.selectedTemplates.includes(templateName)) {
        let index = this.selectedTemplates.indexOf(templateName);
        if (index !== -1) {
          this.selectedTemplates.splice(index, 1);
        }
      } else this.selectedTemplates.push(templateName);
    },
  },
};
</script>
