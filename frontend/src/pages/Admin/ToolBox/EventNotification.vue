<template>
  <div>
    <v-card outlined class="mt-n1">
      <v-card-actions>
        <v-spacer></v-spacer>
        <BaseDialog
          :keep-open="keepDialogOpen"
          title-icon="mdi-bell-alert"
          :title="$t('general.new') + ' ' + $t('events.notification')"
          @submit="createNotification"
        >
          <template v-slot:open="{ open }">
            <TheButton create small @click="open"> {{ $t("events.notification") }}</TheButton>
          </template>
          <template v-slot:default>
            <v-card-text class="mt-2">
              {{ $t("events.new-notification-form-description") }}

              <div class="d-flex justify-space-around mt-1 mb-3">
                <a href="https://github.com/caronc/apprise/wiki" target="_blanks"> Apprise </a>
                <a href="https://github.com/caronc/apprise/wiki/Notify_gotify" target="_blanks"> Gotify </a>
                <a href="https://github.com/caronc/apprise/wiki/Notify_discord" target="_blanks"> Discord </a>
                <a href="https://github.com/caronc/apprise/wiki/Notify_homeassistant" target="_blanks">
                  Home Assistant
                </a>
                <a href="https://github.com/caronc/apprise/wiki/Notify_matrix" target="_blanks"> Matrix </a>
                <a href="https://github.com/caronc/apprise/wiki/Notify_pushover" target="_blanks"> Pushover </a>
              </div>

              <v-form ref="notificationForm">
                <v-select
                  :label="$t('general.type')"
                  :rules="[existsRule]"
                  :items="notificationTypes"
                  item-value="text"
                  v-model="newNotification.type"
                >
                </v-select>
                <v-text-field :rules="[existsRule]" :label="$t('general.name')" v-model="newNotification.name">
                </v-text-field>
                <v-text-field
                  required
                  :rules="[existsRule]"
                  :label="$t('events.apprise-url')"
                  v-model="newNotification.notificationUrl"
                >
                </v-text-field>
                <v-btn class="d-flex ml-auto" small color="info" @click="testByURL(newNotification.notificationUrl)">
                  <v-icon left> mdi-test-tube</v-icon>
                  {{ $t("general.test") }}
                </v-btn>
                <v-subheader class="pa-0 mb-0">
                  {{ $t("events.subscribed-events") }}
                </v-subheader>
                <v-row class="mt-1">
                  <v-col cols="3" v-for="(item, key, index) in newNotificationOptions" :key="index">
                    <v-checkbox class="my-n3 py-0" v-model="newNotificationOptions[key]" :label="key"> </v-checkbox>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>
          </template>
        </BaseDialog>
      </v-card-actions>
      <v-data-table
        disable-sort
        :headers="headers"
        :items="notifications"
        class="elevation-1 text-center"
        :footer-props="{
          'items-per-page-options': [10, 20, 30, 40, -1],
        }"
        :items-per-page="10"
      >
        <template v-for="boolHeader in headers" v-slot:[`item.${boolHeader.value}`]="{ item }">
          <div :key="boolHeader.value">
            <div v-if="boolHeader.value === 'type'">
              <v-avatar size="35" class="ma-1" :color="getIcon(item.type).icon ? 'primary' : undefined">
                <v-icon dark v-if="getIcon(item.type).icon"> {{ getIcon(item.type).icon }}</v-icon>
                <v-img v-else :src="getIcon(item.type).image"> </v-img>
              </v-avatar>
              {{ item[boolHeader.value] }}
            </div>
            <v-icon
              v-else-if="item[boolHeader.value] === true || item[boolHeader.value] === false"
              :color="item[boolHeader.value] ? 'success' : 'gray'"
            >
              {{ item[boolHeader.value] ? "mdi-check" : "mdi-close" }}
            </v-icon>
            <div v-else-if="boolHeader.text === 'Actions'">
              <TheButton class="mr-1" delete x-small minor @click="deleteNotification(item.id)" />
              <TheButton edit x-small @click="testByID(item.id)">
                <template v-slot:icon>
                  mdi-test-tube
                </template>
                {{ $t("general.test") }}
              </TheButton>
            </div>
            <div v-else>
              {{ item[boolHeader.value] }}
            </div>
          </div>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import { api } from "@/api";
import { validators } from "@/mixins/validators";
export default {
  components: {
    BaseDialog,
  },
  mixins: [validators],
  data() {
    return {
      keepDialogOpen: false,
      notifications: [],
      newNotification: {
        type: "General",
        name: "",
        notificationUrl: "",
      },
      newNotificationOptions: {
        general: true,
        recipe: true,
        backup: true,
        scheduled: true,
        migration: true,
        group: true,
        user: true,
      },
      notificationTypes: [
        {
          text: "General",
          icon: "mdi-bell-alert",
        },
        {
          text: "Discord",
          image: "/static/discord.svg",
        },
        {
          text: "Gotify",
          image: "/static/gotify.png",
        },
        {
          text: "Home Assistant",
          image: "/static/home-assistant.png",
        },
        {
          text: "Pushover",
          image: "/static/pushover.svg",
        },
      ],
    };
  },
  mounted() {
    this.getAllNotifications();
  },
  computed: {
    headers() {
      return [
        { text: this.$t("general.type"), value: "type" },
        { text: this.$t("general.name"), value: "name" },
        { text: this.$t("general.general"), value: "general", align: "center" },
        { text: this.$t("general.recipe"), value: "recipe", align: "center" },
        { text: this.$t("events.database"), value: "backup", align: "center" },
        { text: this.$t("events.scheduled"), value: "scheduled", align: "center" },
        { text: this.$t("settings.migrations"), value: "migration", align: "center" },
        { text: this.$t("group.group"), value: "group", align: "center" },
        { text: this.$t("user.user"), value: "user", align: "center" },
        { text: "Actions", align: "center" },
      ];
    },
  },
  methods: {
    getIcon(textValue) {
      return this.notificationTypes.find(x => x.text === textValue);
    },
    async getAllNotifications() {
      this.notifications = await api.about.allEventNotifications();
    },
    async createNotification() {
      if (this.$refs.notificationForm.validate()) {
        this.keepDialogOpen = false;
        await api.about.createNotification({ ...this.newNotification, ...this.newNotificationOptions });
        this.getAllNotifications();
      } else {
        this.keepDialogOpen = true;
      }
    },
    async deleteNotification(id) {
      await api.about.deleteNotification(id);
      this.getAllNotifications();
    },
    async testByID(id) {
      await api.about.testNotificationByID(id);
    },
    async testByURL(url) {
      await api.about.testNotificationByURL(url);
    },
  },
};
</script>

<style scoped>
th {
  text-align: center !important;
}
</style>
