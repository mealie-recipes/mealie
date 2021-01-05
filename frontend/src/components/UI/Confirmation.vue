<template>
  <v-dialog v-model="addRecipe" width="650" @click:outside="reset">
    <v-card :loading="processing">
      <v-card-title class="headline"> From URL </v-card-title>

      <v-card-text> </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" text @click="createRecipe"> Exit </v-btn>
        <v-btn color="primary" text @click="confirm"> Confirm </v-btn>
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
    exit() {
      // do something? 
    }
  },
};
</script>

<style>
</style>