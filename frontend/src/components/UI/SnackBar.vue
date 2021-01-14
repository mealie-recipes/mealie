<template>
  <div class="text-center">
    <v-snackbar :value="active" :timeout="timeout" :color="type">
      {{ text }}

      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="close(false)">
          {{$t('general.close')}}
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
export default {
  data: () => ({
    snackbar: false,
    timeout: -1,
  }),
  computed: {
    text() {
      return this.$store.getters.getSnackText;
    },
    active() {
      return this.$store.getters.getSnackActive;
    },
    type() {
      return this.$store.getters.getSnackType;
    },
  },
  methods: {
    close(value) {
      this.$store.commit("setSnackActive", value);
    },
  },
};
</script>

<style>
</style>