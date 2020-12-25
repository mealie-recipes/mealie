<template>
  <v-row>
    <v-col cols="2"> </v-col>
    <v-col>
      <v-expand-transition>
        <Search class="search-bar" />
      </v-expand-transition>
    </v-col>
    <v-col cols="2">
      <v-btn icon>
        <v-icon> mdi-filter </v-icon>
      </v-btn>
    </v-col>
  </v-row>
</template>

<script>
import Search from "./Search";
export default {
  components: {
    Search,
  },
};
</script>

<style>
</style>