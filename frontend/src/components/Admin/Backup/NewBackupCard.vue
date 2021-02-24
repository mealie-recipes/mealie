<template>
  <v-card :loading="loading">
    <v-card-title> {{ $t("settings.backup.create-heading") }} </v-card-title>
    <v-card-text class="mt-n3">
      <v-text-field
        dense
        :label="$t('settings.backup.backup-tag')"
        v-model="tag"
      ></v-text-field>
    </v-card-text>
    <v-card-actions class="mt-n9 flex-wrap">
      <v-switch v-model="fullBackup" :label="switchLabel"></v-switch>
      <v-spacer></v-spacer>
      <v-btn color="success" text @click="createBackup()">
        {{ $t("general.create") }}
      </v-btn>
    </v-card-actions>

    <v-card-text v-if="!fullBackup" class="mt-n6">
      <v-row>
        <v-col sm="4">
          <p>{{ $t("general.options") }}:</p>
          <v-checkbox
            v-for="option in options"
            :key="option.text"
            class="mb-n4 mt-n3"
            dense
            :label="option.text"
            v-model="option.value"
          ></v-checkbox>
        </v-col>
        <v-col>
          <p>{{ $t("general.templates") }}:</p>
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
  </v-card>
</template>

<script>
import api from "@/api";
export default {
  data() {
    return {
      tag: null,
      fullBackup: true,
      loading: false,
      options: {
        recipes: {
          value: true,
          text: this.$t("general.recipes"),
        },
        settings: {
          value: true,
          text: this.$t("general.settings"),
        },
        themes: {
          value: true,
          text: this.$t("general.themes"),
        },
      },
      availableTemplates: [],
      selectedTemplates: [],
    };
  },
  mounted() {
    this.getAvailableBackups();
  },
  computed: {
    switchLabel() {
      if (this.fullBackup) {
        return this.$t("settings.backup.full-backup");
      } else return this.$t("settings.backup.partial-backup");
    },
  },
  methods: {
    async getAvailableBackups() {
      let response = await api.backups.requestAvailable();
      response.templates.forEach(element => {
        this.availableTemplates.push(element);
      });
    },
    async createBackup() {
      this.loading = true;

      let data = {
        tag: this.tag,
        options: {
          recipes: this.options.recipes.value,
          settings: this.options.settings.value,
          themes: this.options.themes.value,
        },
        templates: this.selectedTemplates,
      };

      await api.backups.create(data);
      this.loading = false;

      this.$emit("created");
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

<style>
</style>