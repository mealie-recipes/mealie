<template>
  <v-dialog
    v-model="dialog"
    :max-width="options.width"
    :style="{ zIndex: options.zIndex }"
    @click:outside="cancel"
    @keydown.esc="cancel"
  >
    <v-card>
      <v-toolbar v-if="Boolean(title)" :color="options.color" dense flat>
        <v-icon v-if="Boolean(options.icon)" left> {{ options.icon }}</v-icon>
        <v-toolbar-title v-text="title" />
      </v-toolbar>

      <v-card-text
        v-show="!!message"
        class="pa-4 text--primary"
        v-html="message"
      />

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey" text @click="cancel"> Cancel </v-btn>
        <v-btn :color="options.color" text @click="confirm"> Confirm </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "Confirmation",
  data: () => ({
    dialog: false, // Wether to show or not
    resolve: null,
    reject: null,
    message: null,
    title: null,
    options: {
      color: "error",
      icon: "mdi-alert-circle",
      width: 400,
      zIndex: 200,
      noconfirm: false,
    },
  }),
  methods: {
    open(title, message, options) {
      this.dialog = true;
      this.title = title;
      this.message = message;
      this.options = Object.assign(this.options, options);
      return new Promise((resolve, reject) => {
        this.resolve = resolve;
        this.reject = reject;
      });
    },

    cancel() {
      this.resolve(false);
      this.dialog = false;
    },

    confirm() {
      this.resolve(true);
      this.dialog = false;
    },
  },
};
</script>

<style>
</style>