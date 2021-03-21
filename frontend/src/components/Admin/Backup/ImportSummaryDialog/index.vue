<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="70%">
      <v-card>
        <v-app-bar dark color="primary mb-2">
          <v-icon large left>
            mdi-import
          </v-icon>
          <v-toolbar-title class="headline">
            Import Summary
          </v-toolbar-title>
          <v-spacer></v-spacer>
        </v-app-bar>
        <v-card-text class="mb-n4">
          <v-row>
            <div>
              <v-card-text>
                <div>
                  <h3>Recipes</h3>
                </div>
                <div class="success--text">
                  Success: {{ recipeNumbers.success }}
                </div>
                <div class="error--text">
                  Failed: {{ recipeNumbers.failure }}
                </div>
              </v-card-text>
            </div>
            <div>
              <v-card-text>
                <div>
                  <h3>Themes</h3>
                </div>
                <div class="success--text">
                  Success: {{ themeNumbers.success }}
                </div>
                <div class="error--text">
                  Failed: {{ themeNumbers.failure }}
                </div>
              </v-card-text>
            </div>
            <div>
              <v-card-text>
                <div>
                  <h3>Settings</h3>
                </div>
                <div class="success--text">
                  Success: {{ settingsNumbers.success }}
                </div>
                <div class="error--text">
                  Failed: {{ settingsNumbers.failure }}
                </div>
              </v-card-text>
            </div>
          </v-row>
        </v-card-text>
        <v-tabs v-model="tab">
          <v-tab>Recipes</v-tab>
          <v-tab>Themes</v-tab>
          <v-tab>Settings</v-tab>
          <v-tab>Users</v-tab>
          <v-tab>Groups</v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
          <v-tab-item>
            <v-card flat>
              <DataTable :data-headers="importHeaders" :data-set="recipeData" />
            </v-card>
          </v-tab-item>
          <v-tab-item>
            <v-card>
              <DataTable
                :data-headers="importHeaders"
                :data-set="themeData"
              /> </v-card
          ></v-tab-item>
          <v-tab-item>
            <v-card
              ><DataTable
                :data-headers="importHeaders"
                :data-set="settingsData"
              />
            </v-card>
          </v-tab-item>
          <v-tab-item>
            <v-card
              ><DataTable :data-headers="importHeaders" :data-set="userData" />
            </v-card>
          </v-tab-item>
          <v-tab-item>
            <v-card
              ><DataTable :data-headers="importHeaders" :data-set="groupData" />
            </v-card>
          </v-tab-item>
        </v-tabs-items>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import DataTable from "./DataTable";
export default {
  components: {
    DataTable,
  },
  data: () => ({
    tab: null,
    dialog: false,
    recipeData: [],
    themeData: [],
    settingsData: [],
    userData: [],
    groupData: [],
    importHeaders: [
      {
        text: "Status",
        value: "status",
      },
      {
        text: "Name",
        align: "start",
        sortable: true,
        value: "name",
      },

      { text: "Exception", value: "data-table-expand", align: "center" },
    ],
    allDataTables: [],
  }),

  computed: {
    recipeNumbers() {
      return this.calculateNumbers(this.recipeData);
    },
    settingsNumbers() {
      return this.calculateNumbers(this.settingsData);
    },
    themeNumbers() {
      return this.calculateNumbers(this.themeData);
    },
    userNumbers() {
      return this.calculateNumbers(this.userData);
    },
    groupNumbers() {
      return this.calculateNumbers(this.groupData);
    },
  },

  methods: {
    calculateNumbers(list_array) {
      if (!list_array) return;
      let numbers = { success: 0, failure: 0 };
      list_array.forEach(element => {
        if (element.status) {
          numbers.success++;
        } else numbers.failure++;
      });
      return numbers;
    },
    open(importData) {
      console.log(importData);
      this.recipeData = importData.recipeImports;
      this.themeData = importData.themeImports;
      this.settingsData = importData.settingsImports;
      this.userData = importData.userImports;
      this.groupData = importData.groupImports;
      this.dialog = true;
    },
  },
};
</script>

<style>
</style>