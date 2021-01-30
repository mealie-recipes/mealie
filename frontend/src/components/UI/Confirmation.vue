
<template>
  <v-dialog
    v-model="dialog"
    :max-width="width"
    :style="{ zIndex: zIndex }"
    @click:outside="cancel"
    @keydown.esc="cancel"
  >
    <v-card>
      <v-toolbar v-if="Boolean(title)" :color="color" dense flat dark>
        <v-icon v-if="Boolean(icon)" left> {{ icon }}</v-icon>
        <v-toolbar-title v-text="title" />
      </v-toolbar>

      <v-card-text
        v-show="!!message"
        class="pa-4 text--primary"
        v-html="message"
      />

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey" text @click="cancel"> {{ $t("general.cancel") }} </v-btn>
        <v-btn :color="color" text @click="confirm"> {{ $t("general.confirm") }} </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
/**
 * Confirmation Component used to add a second validaion step to an action.
 * @version 1.0.1
 * @author [zackbcom](https://github.com/zackbcom)
 * @since Version 1.0.0
 */
export default {
  name: "Confirmation",
  props: {
    /**
     * Message to be in body.
     */
    message: String,
    /**
     * Optional Title message to be used in title.
     */
    title: String,
    /**
     * Optional Icon to be used in title.
     */
    icon: {
      type: String,
      default: "mid-alert-circle"
    },
    /**
     * Color theme of the component. Chose one of the defined theme colors.
     * @values primary, secondary, accent, success, info, warning, error
     */
    color: {
      type: String,
      default: "error"
    },
    /**
     * Define the max width of the component.
     */
    width: {
      type: Number,
      default: 400
    },
    /**
     * zIndex of the component.
     */
    zIndex: {
      type: Number,
      default: 200
    }
  },
  data: () => ({
    /**
     * Keep state of open or closed
     */
    dialog: false
  }),
  methods: {
    /**
     * Sets the modal to be visiable.
     */
    open() {
      this.dialog = true;
    },

    /**
     * Cancel button handler.
     */
    cancel() {
      /**
       * Cancel event.
       *
       * @event Cancel
       * @property {string} content content of the first prop passed to the event
       */
      this.$emit("cancel");

      //Hide Modal
      this.dialog = false;
    },

    /**
     * confirm button handler.
     */
    confirm() {
      /**
       * confirm event.
       *
       * @event confirm
       * @property {string} content content of the first prop passed to the event
       */
      this.$emit("confirm");

      //Hide Modal
      this.dialog = false;
    }
  }
};
</script>

<style>
</style>