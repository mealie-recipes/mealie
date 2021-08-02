<template>
  <v-footer color="primary lighten-1" padless app>
    <v-row justify="center" align="center" dense no-gutters>
      <v-col class="primary py-2 text-center white--text" cols="12">
        <v-btn dark icon href="https://github.com/hay-kot/mealie" target="_blank">
          <v-icon>
            {{ $globals.icons.github }}
          </v-icon>
        </v-btn>
        {{ new Date().getFullYear() }} — <strong>Mealie</strong>
      </v-col>
    </v-row>
  </v-footer>
</template>
      
  <script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  setup() {
    return {};
  },
  data: () => ({
    links: ["Home", "About Us", "Team", "Services", "Blog", "Contact Us"],
  }),
});
</script>
      
      <style scoped>
</style>