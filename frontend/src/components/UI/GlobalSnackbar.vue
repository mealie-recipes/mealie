<template>
  <div class="text-center ma-2">
    <v-snackbar v-model="snackbar.open" top :color="snackbar.color" timeout="3500">
      <v-icon dark left>
        {{ icon }}
      </v-icon>

      {{ snackbar.title }}
      {{ snackbar.text }}

      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar.open = false">
          {{ $t("general.close") }}
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
export default {
  data: () => ({}),
  computed: {
    snackbar: {
      set(val) {
        this.$store.commit("setSnackbar", val);
      },
      get() {
        return this.$store.getters.getSnackbar;
      },
    },
    icon() {
      switch (this.snackbar.color) {
        case "error":
          return "mdi-alert";
        case "success":
          return "mdi-checkbox-marked-circle";
        case "info":
          return "mdi-information";
        default:
          return "mdi-bell-alert";
      }
    },
  },
};
</script>