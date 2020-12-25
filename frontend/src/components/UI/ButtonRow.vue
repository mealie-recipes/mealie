<template>
  <v-toolbar class="card-btn" flat height="0" extension-height="0">
    <template v-slot:extension>
      <v-col></v-col>
      <div v-if="open">
        <v-btn class="mr-2" fab dark small color="error" @click="deleteRecipe">
          <v-icon>mdi-delete</v-icon>
        </v-btn>
        <v-btn class="mr-2" fab dark small color="success" @click="save">
          <v-icon>mdi-content-save</v-icon>
        </v-btn>
        <v-btn class="mr-5" fab dark small color="secondary" @click="json">
          <v-icon>mdi-code-braces</v-icon>
        </v-btn>
      </div>
      <v-btn color="accent" fab dark small @click="editor">
        <v-icon>mdi-square-edit-outline</v-icon>
      </v-btn>
    </template>
  </v-toolbar>
</template>

<script>
export default {
  props: {
    open: {
      default: true,
    },
  },
  methods: {
    editor() {
      this.$emit("editor");
    },
    save() {
      this.$emit("save");
    },
    deleteRecipe() {
      this.$emit("delete");
    },
    json() {
      this.$emit("json");
    },
  },
};
</script>

<style>
</style>