<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-card-title> {{ name }} </v-card-title>
        <v-card-subtitle class="mb-n3"> {{ date }} </v-card-subtitle>
        <v-divider></v-divider>

        <v-card-text>
          <v-row>
            <v-col>
              <v-checkbox
                class="mb-n4 mt-1"
                dense
                label="Import Recipes"
              ></v-checkbox>
              <v-checkbox
                class="my-n4"
                dense
                label="Import Themes"
              ></v-checkbox>
              <v-checkbox
                class="my-n4"
                dense
                label="Import Settings"
              ></v-checkbox>
            </v-col>
            <v-col>
              <v-tooltip top>
                <template v-slot:activator="{ on, attrs }">
                  <span v-on="on" v-bind="attrs">
                    <v-checkbox
                      class="mb-n4 mt-1"
                      dense
                      label="Force"
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
                    ></v-checkbox>
                  </span>
                </template>
                <span
                  >Removes all recipes, and then imports recipes from the
                  backup</span
                >
              </v-tooltip>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-btn color="success" text @click="dialog = false"> Download </v-btn>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="dialog = false"> Delete </v-btn>
          <v-btn color="success" text @click="dialog = false"> Import </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {};
</script>

<script>
export default {
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
      dialog: false,
    };
  },
  methods: {
    open() {
      this.dialog = true;
    },
  },
};
</script>

<style>
</style>