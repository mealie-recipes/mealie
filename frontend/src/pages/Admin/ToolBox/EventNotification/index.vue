<template>
  <div>
    <v-card outlined class="mt-n1">
      <v-card-actions>
        <v-spacer></v-spacer>
        <BaseDialog title-icon="mdi-bell-alert" @submit="createNotification" title="New Notification">
          <template v-slot:open="{ open }">
            <v-btn small color="info" @click="open">
              <v-icon left>
                mdi-plus
              </v-icon>
              Notification
            </v-btn>
          </template>
          <v-card-text class="mt-2">
            We use the <a href="https://github.com/caronc/apprise/wiki" target="_blanks"> Apprise </a> library to
            generate notifications. They offer many options for services to use. Refer to their wiki for a comprehensive
            guide on how to create the URL for your service. If available, selecting the type of your notification can
            include extra features Here are some common choices.

            <div class="d-flex justify-space-around mt-1">
              <a href="https://github.com/caronc/apprise/wiki/Notify_gotify" target="_blanks"> Gotify </a>
              <a href="https://github.com/caronc/apprise/wiki/Notify_discord" target="_blanks"> Discord </a>
              <a href="https://github.com/caronc/apprise/wiki/Notify_homeassistant" target="_blanks">
                Home Assistant
              </a>
              <a href="https://github.com/caronc/apprise/wiki/Notify_matrix" target="_blanks"> Matrix </a>
              <a href="https://github.com/caronc/apprise/wiki/Notify_pushover" target="_blanks"> Pushover </a>
            </div>

            <v-form>
              <v-select label="Type" :items="notificationTypes" item-value="text" v-model="newNotification.type">
              </v-select>
              <v-text-field label="Name" v-model="newNotification.name"> </v-text-field>
              <v-text-field label="Notification URL" v-model="newNotification.notificationUrl"> </v-text-field>
              <v-subheader class="pa-0 mb-0">
                Select the events you would like to recieve notifications for on this URL
              </v-subheader>
              <div class="px-3 dflex row justify-space-between mt-3">
                <v-switch
                  class="ma-0 py-0"
                  v-for="(item, key, index) in newNotificationOptions"
                  :key="index"
                  v-model="newNotificationOptions[key]"
                  :label="key"
                >
                </v-switch>
              </div>
            </v-form>
          </v-card-text>
        </BaseDialog>
      </v-card-actions>
      <v-card-text>
        <v-simple-table>
          <template v-slot:default>
            <thead>
              <tr>
                <th class="text-left">
                  Type
                </th>
                <th class="text-left">
                  Name
                </th>
                <th class="text-left">
                  General
                </th>
                <th class="text-left">
                  Recipe
                </th>
                <th class="text-left">
                  Backup
                </th>
                <th class="text-left">
                  Scheduled
                </th>
                <th class="text-left">
                  Migration
                </th>
                <th class="text-left">
                  Group
                </th>
                <th class="text-left">
                  User
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in notifications" :key="index">
                <td>
                  <v-avatar size="35" class="ma-1" color="primary">
                    <v-icon dark v-if="getIcon(item.type).icon"> {{ getIcon(item.type).icon }}</v-icon>
                    <v-img v-else :src="getIcon(item.type).image"> </v-img>
                  </v-avatar>
                  {{ item.type }}
                </td>
                <td>
                  {{ item.name }}
                </td>
                <td>
                  <v-icon color="success"> {{ item.general ? "mdi-check" : "" }} </v-icon>
                </td>
                <td>
                  <v-icon color="success"> {{ item.recipe ? "mdi-check" : "" }} </v-icon>
                </td>
                <td>
                  <v-icon color="success"> {{ item.backup ? "mdi-check" : "" }} </v-icon>
                </td>
                <td>
                  <v-icon color="success"> {{ item.scheduled ? "mdi-check" : "" }} </v-icon>
                </td>
                <td>
                  <v-icon color="success"> {{ item.migration ? "mdi-check" : "" }} </v-icon>
                </td>
                <td>
                  <v-icon color="success"> {{ item.group ? "mdi-check" : "" }} </v-icon>
                </td>
                <td>
                  <v-icon color="success"> {{ item.user ? "mdi-check" : "" }} </v-icon>
                </td>
                <td>
                  <v-btn small icon color="error" @click="deleteNotification(item.id)">
                    <v-icon> mdi-delete </v-icon>
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import { api } from "@/api";
export default {
  components: {
    BaseDialog,
  },
  data() {
    return {
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
          icon: "mdi-webhook",
        },
        {
          text: "Discord",
          icon: "mdi-discord",
        },
        {
          text: "Gotify",
          image: "./static/gotify.png",
        },
      ],
    };
  },
  mounted() {
    this.getAllNotifications();
  },
  methods: {
    getIcon(textValue) {
      return this.notificationTypes.find(x => x.text === textValue);
    },

    async getAllNotifications() {
      this.notifications = await api.about.allEventNotifications();
    },
    async createNotification() {
      await api.about.createNotification({ ...this.newNotification, ...this.newNotificationOptions });
      this.getAllNotifications();
    },
    async deleteNotification(id) {
      await api.about.deleteNotification(id);
      this.getAllNotifications();
    },
  },
};
</script>

<style lang="scss" scoped>
</style>