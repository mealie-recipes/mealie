<template>
  <v-card flat outlined class="ma-2">
    <v-card-text class="mb-n5 mt-n2">
      <h3>{{ theme.name }} {{ current ? "(Current)" : ""}}</h3>
    </v-card-text>
    <v-card-text>
      <v-row dense>
        <v-card
          v-for="(color, index) in theme.colors"
          :key="index"
          class="mx-1"
          height="34"
          width="36"
          :color="color"
        >
        </v-card>
      </v-row>
    </v-card-text>
    <v-divider></v-divider>
    <v-card-actions>
      <v-btn text color="error">Delete</v-btn>
      <v-spacer></v-spacer>
      <v-btn text color="success">Apply</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  props: {
    theme: Object,
    current: {
      default: false,
    },
  },
};
</script>

<style>
</style>