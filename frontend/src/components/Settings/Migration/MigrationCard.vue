<template>
  <v-card class="my-2" :loading="loading">
    <v-card-title>
      {{ title }}
      <v-spacer></v-spacer>
      <span>
        <UploadBtn
          class="mt-1"
          :url="`/api/migrations/${folder}/upload/`"
          @uploaded="$emit('refresh')"
        />
      </span>
    </v-card-title>
    <v-card-text> {{ description }}</v-card-text>
    <div v-if="available[0]">
      <v-card
        outlined
        v-for="migration in available"
        :key="migration.name"
        class="ma-2"
      >
        <v-card-text>
          <v-row align="center">
            <v-col cols="12" sm="2">
              <v-icon large color="primary"> mdi-import </v-icon>
            </v-col>
            <v-col cols="12" sm="10">
              <div>
                <strong>{{ migration.name }}</strong>
              </div>
              <div>{{ readableTime(migration.date) }}</div>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="mt-n6">
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="deleteMigration(migration.name)">
            {{ $t("general.delete") }}
          </v-btn>
          <v-btn color="accent" text @click="importMigration(migration.name)">
            {{ $t("general.import") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
    <div v-else>
      <v-card class="text-center ma-2">
        <v-card-text>
          {{ $t("migration.no-migration-data-available") }}
        </v-card-text>
      </v-card>
    </div>
    <br />
  </v-card>
</template>

<script>
import UploadBtn from "../../UI/UploadBtn";
import utils from "../../../utils";
import api from "../../../api";
export default {
  props: {
    folder: String,
    title: String,
    description: String,
    available: Array,
  },
  components: {
    UploadBtn,
  },
  data() {
    return {
      loading: false,
    };
  },
  methods: {
    deleteMigration(file_name) {
      api.migrations.delete(this.folder, file_name);
      this.$emit("refresh");
    },
    async importMigration(file_name) {
      this.loading == true;
      let response = await api.migrations.import(this.folder, file_name);
      this.$emit("imported", response.successful, response.failed);
      this.loading == false;
    },
    readableTime(timestamp) {
      let date = new Date(timestamp);
      return utils.getDateAsText(date);
    },
  },
};
</script>

<style>
</style>