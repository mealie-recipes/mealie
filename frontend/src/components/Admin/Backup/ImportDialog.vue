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
          <v-row>
            <v-col>
              <ImportOptions @update-options="updateOptions" class="mt-5" />
            </v-col>
            <!-- <v-col>
              <v-tooltip top>
                <template v-slot:activator="{ on, attrs }">
                  <span v-on="on" v-bind="attrs">
                    <v-checkbox
                      class="mb-n4 mt-1"
                      dense
                      label="Force"
                      v-model="forceImport"
                    ></v-checkbox>
                  </span>
                </template>
                <span>Force update existing recipes</span>
              </v-tooltip>
              <v-tooltip top>
                <template v-slot:activator="{ on, attrs }">
                  <span v-on="on" v-bind="attrs">
                    <v-checkbox
                      class="mb-n4 mt-1"
                      dense
                      label="Rebase"
                      v-model="rebaseImport"
                    ></v-checkbox>
                  </span>
                </template>
                <span
                  >Removes all recipes, and then imports recipes from the
                  backup</span
                >
              </v-tooltip>
            </v-col> -->
          </v-row>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-btn color="accent" text :href="`/api/backups/${name}/download`">
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
  },
};
</script>

<style>
</style>