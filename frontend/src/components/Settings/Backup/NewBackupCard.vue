<template>
  <v-card :loading="loading">
    <v-card-title> Create a Backup </v-card-title>

    <v-card-actions class="mt-n6">
      <v-switch v-model="fullBackup" :label="switchLabel"></v-switch>
      <v-spacer></v-spacer>
      <v-btn color="success" text @click="createBackup()"> Create </v-btn>
    </v-card-actions>

    <v-card-text v-if="!fullBackup" class="mt-n6">
      <v-row>
        <v-col sm="4">
          <p>Options:</p>
          <v-checkbox
            class="mb-n4 mt-n3"
            dense
            label="Recipes"
            v-model="importRecipes"
          ></v-checkbox>
          <v-checkbox
            class="my-n4"
            dense
            label="Themes"
            v-model="importThemes"
          ></v-checkbox>
          <v-checkbox
            class="my-n4"
            dense
            label="Settings"
            v-model="importThemes"
          ></v-checkbox>
        </v-col>
        <v-col>
          <p>Templates:</p>
          <v-checkbox
            class="mb-n4 mt-n3"
            dense
            label="Template asdfasdf"
            v-model="importRecipes"
          ></v-checkbox>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  data() {
    return {
      fullBackup: true,
      loading: false,
    };
  },
  computed: {
    switchLabel() {
      if (this.fullBackup) {
        return "Full Backup";
      } else return "Partial Backup";
    },
  },
  methods: {
    createBackup() {
      this.loading = true;
    },
  },
};
</script>

<style>
</style>