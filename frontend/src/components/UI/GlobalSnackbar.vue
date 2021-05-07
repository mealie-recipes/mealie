<template>
  <div class="text-center ma-2">
    <v-snackbar v-model="snackbar.open" top :color="snackbar.color" timeout="3500">
      {{ snackbar.title }}
      {{ snackbar.text }}

      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar.open = false">
          {{ $t("general.cancel") }}
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
        console.log(this.$store.getters.getSnackbar);
        return this.$store.getters.getSnackbar;
      },
    },
  },
};
</script>