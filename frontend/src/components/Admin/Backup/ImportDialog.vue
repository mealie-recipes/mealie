<template>
  <div class="text-center">
    <v-dialog
      v-model="dialog"
      width="500"
      :fullscreen="$vuetify.breakpoint.xsOnly"
    >
      <v-card>
        <v-toolbar dark color="primary" v-show="$vuetify.breakpoint.xsOnly">
          <v-btn icon dark @click="dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title></v-toolbar-title>
          <v-spacer></v-spacer>
          <v-toolbar-items>
            <v-btn dark text @click="raiseEvent('import')">
              {{ $t("general.import") }}
            </v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <v-card-title> {{ name }} </v-card-title>
        <v-card-subtitle class="mb-n3"> {{ date }} </v-card-subtitle>
        <v-divider></v-divider>

        <v-card-text>
          <ImportOptions @update-options="updateOptions" class="mt-5 mb-2" />

          <v-divider></v-divider>

          <v-checkbox
            dense
            label="Remove existing entries matching imported entries"
            v-model="forceImport"
          ></v-checkbox>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-btn
            color="accent"
            text
            :loading="downloading"
            @click="downloadFile(`/api/backups/${name}/download`)"
          >
            {{ $t("general.download") }}
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="raiseEvent('delete')">
            {{ $t("general.delete") }}
          </v-btn>
          <v-btn
            color="success"
            outlined
            @click="raiseEvent('import')"
            v-show="$vuetify.breakpoint.smAndUp"
          >
            {{ $t("general.import") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>


<script>
import ImportOptions from "@/components/Admin/Backup/ImportOptions";
import axios from "axios";
export default {
  components: { ImportOptions },
  props: {
    name: {
      default: "Backup Name",
    },
    date: {
      default: "Backup Date",
    },
  },
  data() {
    return {
      options: {
        recipes: true,
        settings: true,
        themes: true,
        users: true,
        groups: true,
      },
      dialog: false,
      forceImport: false,
      rebaseImport: false,
      downloading: false,
    };
  },
  methods: {
    updateOptions(options) {
      this.options = options;
    },
    open() {
      this.dialog = true;
    },
    close() {
      this.dialog = false;
    },
    raiseEvent(event) {
      let eventData = {
        name: this.name,
        force: this.forceImport,
        rebase: this.rebaseImport,
        recipes: this.options.recipes,
        settings: this.options.settings,
        themes: this.options.themes,
        users: this.options.users,
        groups: this.options.groups,
      };
      this.close();
      this.$emit(event, eventData);
    },
    async downloadFile(downloadURL) {
      this.downloading = true;
      const response = await axios({
        url: downloadURL,
        method: "GET",
        responseType: "blob", // important
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${this.name}.zip`);
      document.body.appendChild(link);
      link.click();

      this.downloading = false;
    },
  },
};
</script>

<style>
</style>