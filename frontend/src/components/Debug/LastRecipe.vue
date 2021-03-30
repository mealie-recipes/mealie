<template>
  <v-card>
    <v-card-title>Last Scrapped JSON Data</v-card-title>
    <v-card-text>
      <VJsoneditor
        @error="logError()"
        v-model="lastRecipeJson"
        height="1500px"
        :options="jsonEditorOptions"
      />
    </v-card-text>
  </v-card>
</template>

<script>
import VJsoneditor from "v-jsoneditor";
import { api } from "@/api";
export default {
  components: { VJsoneditor },
  data() {
    return {
      lastRecipeJson: {},
      jsonEditorOptions: {
        mode: "code",
        search: false,
        mainMenuBar: false,
      },
    };
  },

  async mounted() {
    this.lastRecipeJson = await api.meta.getLastJson();
  },
};
</script>

<style>
</style>