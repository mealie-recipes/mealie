<template>
  <div>
    <ConfirmationDialog
      :title="$t('settings.theme.delete-theme')"
      :message="$t('settings.theme.are-you-sure-you-want-to-delete-this-theme')"
      color="error"
      icon="mdi-alert-circle"
      ref="deleteThemeConfirm"
      v-on:confirm="deleteSelectedTheme()"
    />
    <v-card flat outlined class="ma-2">
      <v-card-text class="mb-n5 mt-n2">
        <h3>
          {{ theme.name }}
          {{ current ? $t("general.current-parenthesis") : "" }}
        </h3>
      </v-card-text>
      <v-card-text>
        <v-row flex align-center>
          <v-card
            v-for="(color, index) in theme.colors"
            :key="index"
            class="ma-1 mx-auto"
            height="34"
            width="36"
            :color="color"
          >
          </v-card>
        </v-row>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-btn text color="error" @click="confirmDelete">
          {{ $t("general.delete") }}
        </v-btn>
        <v-spacer></v-spacer>
        <!-- <v-btn text color="accent" @click="editTheme">Edit</v-btn> -->
        <v-btn text color="success" @click="saveThemes">{{
          $t("general.apply")
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import ConfirmationDialog from "@/components/UI/Dialogs/ConfirmationDialog";
import { api } from "@/api";
import utils from "@/utils";

const DELETE_EVENT = "delete";
const APPLY_EVENT = "apply";
const EDIT_EVENT = "edit";
export default {
  components: {
    ConfirmationDialog,
  },
  props: {
    theme: Object,
    current: {
      default: false,
    },
  },
  methods: {
    confirmDelete() {
      if (this.theme.name === "default") {
        // Notify User Can't Delete Default
      } else if (this.theme !== {}) {
        this.$refs.deleteThemeConfirm.open();
      }
    },
    async deleteSelectedTheme() {
      //Delete Theme from DB
      const response = await api.themes.delete(this.theme.name);
      if (response.status != 200) {
        utils.notify.error(this.$t('settings.theme.error-deleting-theme'));
      } else {
        utils.notify.success(this.$t('settings.theme.theme-deleted'));
        //Get the new list of available from DB
        this.availableThemes = await api.themes.requestAll();
        this.$emit(DELETE_EVENT);
      }
    },
    async saveThemes() {
      this.$store.commit("setTheme", this.theme);
      this.$emit(APPLY_EVENT, this.theme);
    },
    editTheme() {
      this.$emit(EDIT_EVENT);
    },
  },
};
</script>

<style>
</style>