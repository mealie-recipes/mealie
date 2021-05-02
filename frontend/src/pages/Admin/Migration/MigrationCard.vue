<template>
  <v-card outlined class="my-2" :loading="loading">
    <MigrationDialog ref="migrationDialog" />
    <v-card-title>
      {{ title }}
      <v-spacer></v-spacer>
      <span>
        <TheUploadBtn
          class="mt-1"
          :url="`/api/migrations/${folder}/upload`"
          fileName="archive"
          @uploaded="$emit('refresh')"
          :post="true"
        />
      </span>
    </v-card-title>
    <v-card-text> {{ description }}</v-card-text>
    <div v-if="available[0]">
      <v-card outlined v-for="migration in available" :key="migration.name" class="ma-2">
        <v-card-text>
          <v-row align="center">
            <v-col cols="2">
              <v-icon large color="primary">mdi-import</v-icon>
            </v-col>
            <v-col cols="10">
              <div class="text-truncate">
                <strong>{{ migration.name }}</strong>
              </div>
              <div class="text-truncate">
                {{ $d(new Date(migration.date), "medium") }}
              </div>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="mt-n6">
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="deleteMigration(migration.name)">
            {{ $t("general.delete") }}
          </v-btn>
          <v-btn color="accent" text @click="importMigration(migration.name)" :loading="loading" :disabled="loading">
            {{ $t("general.import") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
    <div v-else>
      <v-card outlined class="text-center ma-2">
        <v-card-text>
          {{ $t("migration.no-migration-data-available") }}
        </v-card-text>
      </v-card>
    </div>
    <br />
  </v-card>
</template>

<script>
import TheUploadBtn from "@/components/UI/Buttons/TheUploadBtn";
import { api } from "@/api";
import MigrationDialog from "./MigrationDialog";
export default {
  props: {
    folder: String,
    title: String,
    description: String,
    available: Array,
  },
  components: {
    TheUploadBtn,
    MigrationDialog,
  },
  data() {
    return {
      loading: false,
    };
  },
  methods: {
    async deleteMigration(file_name) {
      if (await api.migrations.delete(this.folder, file_name)) {
        this.$emit("refresh");
      }
    },
    async importMigration(file_name) {
      this.loading = true;
      let response = await api.migrations.import(this.folder, file_name);
      this.$refs.migrationDialog.open(response);
      // this.$emit("imported", response.successful, response.failed);
      this.loading = false;
    },
  },
};
</script>

<style></style>
