<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="70%">
      <v-card>
        <v-card-title> Import Summary </v-card-title>
        <v-card-text>
          <v-row class="mb-n9">
            <v-card flat>
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
            </v-card>
            <v-card flat>
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
            </v-card>
            <v-card flat>
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
            </v-card>
          </v-row>
        </v-card-text>
        <v-tabs v-model="tab">
          <v-tab>Recipes</v-tab>
          <v-tab>Themes</v-tab>
          <v-tab>Settings</v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
          <v-tab-item>
            <v-card flat>
              <DataTable :data-headers="recipeHeaders" :data-set="recipeData" />
            </v-card>
          </v-tab-item>
          <v-tab-item>
            <v-card>
              <DataTable
                :data-headers="recipeHeaders"
                :data-set="themeData"
              /> </v-card
          ></v-tab-item>
          <v-tab-item>
            <v-card
              ><DataTable
                :data-headers="recipeHeaders"
                :data-set="settingsData"
              />
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
    recipeHeaders: [
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
      let numbers = { success: 0, failure: 0 };
      this.recipeData.forEach(element => {
        if (element.status) {
          numbers.success++;
        } else numbers.failure++;
      });
      return numbers;
    },
    settingsNumbers() {
      let numbers = { success: 0, failure: 0 };
      this.settingsData.forEach(element => {
        if (element.status) {
          numbers.success++;
        } else numbers.failure++;
      });
      return numbers;
    },
    themeNumbers() {
      let numbers = { success: 0, failure: 0 };
      this.themeData.forEach(element => {
        if (element.status) {
          numbers.success++;
        } else numbers.failure++;
      });
      return numbers;
    },
  },

  methods: {
    open(importData) {
      this.recipeData = importData.recipeImports;
      this.themeData = importData.themeReport;
      this.settingsData = importData.settingsReport;
      this.dialog = true;
    },
  },
};
</script>

<style>
</style>