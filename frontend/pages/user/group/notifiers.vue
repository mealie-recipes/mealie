<template>
  <v-container class="narrow-container">
    <BaseDialog
      v-model="deleteDialog"
      color="error"
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      @confirm="deleteNotifier(deleteTargetId)"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>
    <BaseDialog v-model="createDialog" title="New Notification" @submit="createNewNotifier">
      <v-card-text>
        <v-text-field v-model="createNotifierData.name" :label="$t('general.name')"></v-text-field>
        <v-text-field v-model="createNotifierData.appriseUrl" :label="$t('events.apprise-url')"></v-text-field>
      </v-card-text>
    </BaseDialog>

    <BasePageTitle divider>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-notifiers.svg')"></v-img>
      </template>
      <template #title> Event Notifiers </template>
      {{ $t("events.new-notification-form-description") }}

      <div class="mt-3 d-flex justify-space-around">
        <a href="https://github.com/caronc/apprise/wiki" target="_blanks"> Apprise </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_gotify" target="_blanks"> Gotify </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_discord" target="_blanks"> Discord </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_homeassistant" target="_blanks"> Home Assistant </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_matrix" target="_blanks"> Matrix </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_pushover" target="_blanks"> Pushover </a>
      </div>
    </BasePageTitle>

    <BannerExperimental issue="https://github.com/hay-kot/mealie/issues/833" />

    <BaseButton create @click="createDialog = true" />
    <v-expansion-panels v-if="notifiers" class="mt-2">
      <v-expansion-panel v-for="(notifier, index) in notifiers" :key="index" class="my-2 left-border rounded">
        <v-expansion-panel-header disable-icon-rotate class="headline">
          <div class="d-flex align-center">
            {{ notifier.name }}
          </div>
          <template #actions>
            <v-btn icon class="ml-2">
              <v-icon>
                {{ $globals.icons.edit }}
              </v-icon>
            </v-btn>
          </template>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-text-field v-model="notifiers[index].name" label="Name"></v-text-field>
          <v-text-field v-model="notifiers[index].appriseUrl" label="Apprise URL (skipped in blank)"></v-text-field>
          <v-checkbox v-model="notifiers[index].enabled" label="Enable Notifier" dense></v-checkbox>

          <v-divider></v-divider>
          <p class="pt-4">What events should this notifier subscribe to?</p>
          <template v-for="(opt, idx) in optionsKeys">
            <v-checkbox
              v-if="!opt.divider"
              :key="'option-' + idx"
              v-model="notifiers[index].options[opt.key]"
              hide-details
              dense
              :label="opt.text"
            ></v-checkbox>
            <div v-else :key="'divider-' + idx" class="mt-4">
              {{ opt.text }}
            </div>
          </template>
          <v-card-actions class="py-0">
            <v-spacer></v-spacer>
            <BaseButtonGroup
              :buttons="[
                {
                  icon: $globals.icons.delete,
                  text: $t('general.delete'),
                  event: 'delete',
                },
                {
                  icon: $globals.icons.testTube,
                  text: $t('general.test'),
                  event: 'test',
                },
                {
                  icon: $globals.icons.save,
                  text: $t('general.save'),
                  event: 'save',
                },
              ]"
              @delete="openDelete(notifier)"
              @save="saveNotifier(notifier)"
              @test="testNotifier(notifier)"
            />
          </v-card-actions>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>
<script lang="ts">
import { defineComponent, useAsync, reactive, useContext, toRefs } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { useAsyncKey } from "~/composables/use-utils";
import { GroupEventNotifierCreate, GroupEventNotifierOut } from "~/types/api-types/group";

interface OptionKey {
  text: string;
  key: string;
}

interface OptionDivider {
  divider: true;
  text: string;
}

export default defineComponent({
  setup() {
    const api = useUserApi();

    const state = reactive({
      deleteDialog: false,
      createDialog: false,
      deleteTargetId: "",
    });

    const notifiers = useAsync(async () => {
      const { data } = await api.groupEventNotifier.getAll();
      return data ?? [];
    }, useAsyncKey());

    async function refreshNotifiers() {
      const { data } = await api.groupEventNotifier.getAll();
      notifiers.value = data ?? [];
    }

    const createNotifierData: GroupEventNotifierCreate = reactive({
      name: "",
      enabled: true,
      appriseUrl: "",
    });

    async function createNewNotifier() {
      await api.groupEventNotifier.createOne(createNotifierData);
      refreshNotifiers();
    }

    function openDelete(notifier: GroupEventNotifierOut) {
      state.deleteDialog = true;
      state.deleteTargetId = notifier.id;
    }

    async function deleteNotifier(targetId: string) {
      await api.groupEventNotifier.deleteOne(targetId);
      refreshNotifiers();
      state.deleteTargetId = "";
    }

    async function saveNotifier(notifier: GroupEventNotifierOut) {
      await api.groupEventNotifier.updateOne(notifier.id, notifier);
      refreshNotifiers();
    }

    async function testNotifier(notifier: GroupEventNotifierOut) {
      await api.groupEventNotifier.test(notifier.id);
    }

    // ===============================================================
    // Options Definitions
    const { i18n } = useContext();

    const optionsKeys: (OptionKey | OptionDivider)[] = [
      {
        divider: true,
        text: "Recipe Events",
      },
      {
        text: i18n.t("general.create") as string,
        key: "recipeCreated",
      },
      {
        text: i18n.t("general.update") as string,
        key: "recipeUpdated",
      },
      {
        text: i18n.t("general.delete") as string,
        key: "recipeDeleted",
      },
      {
        divider: true,
        text: "User Events",
      },
      {
        text: "When a new user joins your group",
        key: "userSignup",
      },
      {
        divider: true,
        text: "Data Events",
      },
      {
        text: "When a new data migration is completed",
        key: "dataMigrations",
      },
      {
        text: "When a data export is completed",
        key: "dataExport",
      },
      {
        text: "When a data import is completed",
        key: "dataImport",
      },
      {
        divider: true,
        text: "Mealplan Events",
      },
      {
        text: "When a user in your group creates a new mealplan",
        key: "mealplanEntryCreated",
      },
      {
        divider: true,
        text: "Shopping List Events",
      },
      {
        text: i18n.t("general.create") as string,
        key: "shoppingListCreated",
      },
      {
        text: i18n.t("general.update") as string,
        key: "shoppingListUpdated",
      },
      {
        text: i18n.t("general.delete") as string,
        key: "shoppingListDeleted",
      },
      {
        divider: true,
        text: "Cookbook Events",
      },
      {
        text: i18n.t("general.create") as string,
        key: "cookbookCreated",
      },
      {
        text: i18n.t("general.update") as string,
        key: "cookbookUpdated",
      },
      {
        text: i18n.t("general.delete") as string,
        key: "cookbookDeleted",
      },
      {
        divider: true,
        text: "Tag Events",
      },
      {
        text: i18n.t("general.create") as string,
        key: "tagCreated",
      },
      {
        text: i18n.t("general.update") as string,
        key: "tagUpdated",
      },
      {
        text: i18n.t("general.delete") as string,
        key: "tagDeleted",
      },
      {
        divider: true,
        text: "Category Events",
      },
      {
        text: i18n.t("general.create") as string,
        key: "categoryCreated",
      },
      {
        text: i18n.t("general.update") as string,
        key: "categoryUpdated",
      },
      {
        text: i18n.t("general.delete") as string,
        key: "categoryDeleted",
      },
    ];

    return {
      ...toRefs(state),
      openDelete,
      optionsKeys,
      notifiers,
      createNotifierData,
      deleteNotifier,
      testNotifier,
      saveNotifier,
      createNewNotifier,
    };
  },
  head: {
    title: "Notifiers",
  },
});
</script>
