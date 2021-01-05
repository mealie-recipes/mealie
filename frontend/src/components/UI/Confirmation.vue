<template>
  <v-dialog v-model="addRecipe" width="650" @click:outside="reset">
    <v-card :loading="processing">
      <v-card-title class="headline"> From URL </v-card-title>

      <v-card-text>
        <v-form>
          <v-text-field v-model="recipeURL" label="Recipe URL"></v-text-field>
        </v-form>

        <v-alert v-if="error" color="red" outlined type="success">
          Looks like there was an error parsing the URL. Check the log and
          debug/last_recipe.json to see what went wrong.
        </v-alert>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" text @click="createRecipe"> Submit </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    type: String,
  },
  data() {
    return {};
  },
  methods: {
    confirm() {
      this.$emit("confirm");
    },
  },
};
</script>

<style>
</style>