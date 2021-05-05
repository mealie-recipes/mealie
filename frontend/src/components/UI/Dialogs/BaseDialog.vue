<template>
  <div>
    <slot name="open" v-bind="{ open }"> </slot>
    <v-dialog v-model="dialog" :width="modalWidth + 'px'" :content-class="top ? 'top-dialog' : undefined">
      <v-card class="pb-10" height="100%">
        <v-app-bar dark :color="color" class="mt-n1 mb-0">
          <v-icon large left>
            {{ titleIcon }}
          </v-icon>
          <v-toolbar-title class="headline"> {{ title }} </v-toolbar-title>
          <v-spacer></v-spacer>
        </v-app-bar>
        <v-progress-linear class="mt-1" v-if="loading" indeterminate color="primary"></v-progress-linear>
        <slot> </slot>
        <v-card-actions>
          <slot name="card-actions">
            <v-btn text color="grey" @click="dialog = false">
              {{ $t("general.cancel") }}
            </v-btn>
            <v-spacer></v-spacer>

            <v-btn color="error" text @click="deleteEvent" v-if="$listeners.delete">
              {{ $t("general.delete") }}
            </v-btn>
            <v-btn color="success" @click="submitEvent">
              {{ submitText }}
            </v-btn>
          </slot>
        </v-card-actions>

        <slot name="below-actions"> </slot>
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
      default: "mdi-account",
    },
    modalWidth: {
      default: "500",
    },
    loading: {
      default: false,
    },
    top: {
      default: false,
    },
    submitText: {
      default: () => i18n.t("general.create"),
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
      return this.submitted && !this.loading;
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

<style scoped>
.top-dialog {
  align-self: flex-start;
}
</style>
