<template>
  <v-container fluid>
    <BaseCardSectionTitle title="Event Notifications">
      {{ $t("events.new-notification-form-description") }}

      <div class="d-flex justify-space-around">
        <a href="https://github.com/caronc/apprise/wiki" target="_blanks"> Apprise </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_gotify" target="_blanks"> Gotify </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_discord" target="_blanks"> Discord </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_homeassistant" target="_blanks"> Home Assistant </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_matrix" target="_blanks"> Matrix </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_pushover" target="_blanks"> Pushover </a>
      </div>
    </BaseCardSectionTitle>

    <BaseDialog
      ref="domDeleteConfirmation"
      :title="$t('settings.backup.delete-backup')"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="deleteNotification()"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <v-toolbar color="background" flat class="justify-between">
      <BaseDialog
        :icon="$globals.icons.bellAlert"
        :title="$t('general.new') + ' ' + $t('events.notification')"
        @submit="createNotification"
      >
        <template #activator="{ open }">
          <BaseButton @click="open"> {{ $t("events.notification") }}</BaseButton>
        </template>

        <v-card-text>
          <v-select
            v-model="createNotificationData.type"
            :items="notificationTypes"
            :label="$t('general.type')"
          ></v-select>
          <v-text-field v-model="createNotificationData.name" :label="$t('general.name')"></v-text-field>
          <v-text-field
            v-model="createNotificationData.notificationUrl"
            :label="$t('events.apprise-url')"
          ></v-text-field>

          <BaseButton
            class="d-flex ml-auto"
            small
            color="info"
            @click="testByUrl(createNotificationData.notificationUrl)"
          >
            <template #icon> {{ $globals.icons.testTube }}</template>
            {{ $t("general.test") }}
          </BaseButton>

          <p class="text-uppercase">{{ $t("events.subscribed-events") }}</p>
          <div class="d-flex flex-wrap justify-center">
            <v-checkbox
              v-model="createNotificationData.general"
              class="mb-n2 mt-n2 mx-2"
              :label="$t('general.general')"
            ></v-checkbox>
            <v-checkbox
              v-model="createNotificationData.recipe"
              class="mb-n2 mt-n2 mx-2"
              :label="$t('general.recipe')"
            ></v-checkbox>
            <v-checkbox
              v-model="createNotificationData.backup"
              class="mb-n2 mt-n2 mx-2"
              :label="$t('settings.backup-and-exports')"
            ></v-checkbox>
            <v-checkbox
              v-model="createNotificationData.scheduled"
              class="mb-n2 mt-n2 mx-2"
              :label="$t('events.scheduled')"
            ></v-checkbox>
            <v-checkbox
              v-model="createNotificationData.migration"
              class="mb-n2 mt-n2 mx-2"
              :label="$t('settings.migrations')"
            ></v-checkbox>
            <v-checkbox
              v-model="createNotificationData.group"
              class="mb-n2 mt-n2 mx-2"
              :label="$t('group.group')"
            ></v-checkbox>
            <v-checkbox
              v-model="createNotificationData.user"
              class="mb-n2 mt-n2 mx-2"
              :label="$t('user.user')"
            ></v-checkbox>
          </div>
        </v-card-text>
      </BaseDialog>
    </v-toolbar>

    <!-- Data Table -->
    <v-data-table
      :headers="headers"
      :items="notifications || []"
      class="elevation-0"
      hide-default-footer
      disable-pagination
    >
      <template v-for="boolHeader in headers" #[`item.${boolHeader.value}`]="{ item }">
        <div :key="boolHeader.value">
          <div v-if="boolHeader.value === 'type'">
            {{ item[boolHeader.value] }}
          </div>
          <v-icon
            v-else-if="item[boolHeader.value] === true || item[boolHeader.value] === false"
            :color="item[boolHeader.value] ? 'success' : 'gray'"
          >
            {{ item[boolHeader.value] ? $globals.icons.check : $globals.icons.close }}
          </v-icon>
          <div v-else-if="boolHeader.value === 'actions'" class="d-flex">
            <BaseButton
              class="mr-1"
              delete
              x-small
              minor
              @click="
                deleteTarget = item.id;
                domDeleteConfirmation.open();
              "
            />
            <BaseButton edit x-small @click="testById(item.id)">
              <template #icon>
                {{ $globals.icons.testTube }}
              </template>
              {{ $t("general.test") }}
            </BaseButton>
          </div>
          <div v-else>
            {{ item[boolHeader.value] }}
          </div>
        </div>
      </template>
    </v-data-table>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, useContext, toRefs, ref } from "@nuxtjs/composition-api";
import { useNotifications } from "@/composables/use-notifications";
export default defineComponent({
  layout: "admin",
  setup() {
    const { i18n } = useContext();

    const state = reactive({
      headers: [
        { text: i18n.t("general.type"), value: "type" },
        { text: i18n.t("general.name"), value: "name" },
        { text: i18n.t("general.general"), value: "general", align: "center" },
        { text: i18n.t("general.recipe"), value: "recipe", align: "center" },
        { text: i18n.t("events.database"), value: "backup", align: "center" },
        { text: i18n.t("events.scheduled"), value: "scheduled", align: "center" },
        { text: i18n.t("settings.migrations"), value: "migration", align: "center" },
        { text: i18n.t("group.group"), value: "group", align: "center" },
        { text: i18n.t("user.user"), value: "user", align: "center" },
        { text: "", value: "actions" },
      ],
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
    });

    const {
      deleteNotification,
      createNotification,
      refreshNotifications,
      notifications,
      loading,
      testById,
      testByUrl,
      createNotificationData,
      notificationTypes,
      deleteTarget,
    } = useNotifications();

    // API
    const domDeleteConfirmation = ref(null);
    return {
      ...toRefs(state),
      domDeleteConfirmation,
      notifications,
      loading,
      createNotificationData,
      deleteNotification,
      deleteTarget,
      createNotification,
      refreshNotifications,
      testById,
      testByUrl,
      notificationTypes,
    };
  },
  head() {
    return {
      title: this.$t("events.notification") as string,
    };
  },
});
</script>

<style scoped>
</style>
