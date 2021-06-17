<template>
  <div>
    <slot name="open" v-bind="{ open }"> </slot>
    <v-dialog
      v-model="dialog"
      :width="modalWidth + 'px'"
      :content-class="top ? 'top-dialog' : undefined"
      :fullscreen="$vuetify.breakpoint.xsOnly"
    >
      <v-card height="100%">
        <v-app-bar dark :color="color" class="mt-n1 mb-0">
          <v-icon large left>
            {{ displayTitleIcon }}
          </v-icon>
          <v-toolbar-title class="headline"> {{ title }} </v-toolbar-title>
          <v-spacer></v-spacer>
        </v-app-bar>
        <v-progress-linear class="mt-1" v-if="loading" indeterminate color="primary"></v-progress-linear>

        <slot v-bind="{ submitEvent }"> </slot>

        <v-card-actions>
          <slot name="card-actions">
            <v-btn text color="grey" @click="dialog = false">
              {{ $t("general.cancel") }}
            </v-btn>
            <v-spacer></v-spacer>

            <v-btn color="error" text @click="deleteEvent" v-if="$listeners.delete">
              {{ $t("general.delete") }}
            </v-btn>
            <slot name="extra-buttons"> </slot>
            <v-btn color="success" type="submit" @click="submitEvent">
              {{ submitText }}
            </v-btn>
          </slot>
        </v-card-actions>

        <div class="pb-4" v-if="$slots['below-actions']">
          <slot name="below-actions"> </slot>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import i18n from "@/i18n";
export default {
  props: {
    color: {
      default: "primary",
    },
    title: {
      default: "Modal Title",
    },
    titleIcon: {
      default: null,
    },
    modalWidth: {
      default: "500",
    },
    loading: {
      default: false,
    },
    top: {
      default: null,
    },
    submitText: {
      default: () => i18n.t("general.create"),
    },
    keepOpen: {
      default: false,
    },
  },
  data() {
    return {
      dialog: false,
      submitted: false,
    };
  },
  computed: {
    determineClose() {
      return this.submitted && !this.loading && !this.keepOpen;
    },
    displayTitleIcon() {
      return this.titleIcon || this.$globals.icons.user;
    },
  },
  watch: {
    determineClose() {
      this.submitted = false;
      this.dialog = false;
    },
    dialog(val) {
      if (val) this.submitted = false;
    },
  },
  methods: {
    submitEvent() {
      this.$emit("submit");
      this.submitted = true;
    },
    open() {
      this.dialog = true;
    },
    close() {
      this.dialog = false;
    },
    deleteEvent() {
      this.$emit("delete");
      this.submitted = true;
    },
  },
};
</script>

<style>
</style>
