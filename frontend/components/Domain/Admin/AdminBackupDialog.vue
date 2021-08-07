<template>
  <div>
    <BaseDialog
      :title="$t('settings.backup.create-heading')"
      :title-icon="$globals.icons.database"
      :submit-text="$t('general.create')"
      :loading="loading"
      @submit="createBackup"
    >
      <template #open="{ open }">
        <v-btn class="mx-2" small :color="color" @click="open">
          <v-icon left> {{ $globals.icons.create }} </v-icon> {{ $t("general.custom") }}
        </v-btn>
      </template>
      <v-card-text class="mt-6">
        <v-text-field v-model="tag" dense :label="$t('settings.backup.backup-tag')"></v-text-field>
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
                <AdminBackupImportOptions v-model="updateOptions" class="mt-5" />
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
import AdminBackupImportOptions from "./AdminBackupImportOptions";
export default {
  components: {
    AdminBackupImportOptions,
  },
  props: {
    color: {
      type: String,
      default: "primary",
    },
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
  created() {
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
        notifications: true,
      };
      this.availableTemplates = [];
      this.selectedTemplates = [];
    },
    updateOptions(options) {
      this.options = options;
    },
    async getAvailableBackups() {
      const response = await api.backups.requestAvailable();
      response.templates.forEach((element) => {
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
          notifications: this.options.notifications,
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
        const index = this.selectedTemplates.indexOf(templateName);
        if (index !== -1) {
          this.selectedTemplates.splice(index, 1);
        }
      } else this.selectedTemplates.push(templateName);
    },
  },
};
</script>
