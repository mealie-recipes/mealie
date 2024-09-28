<template>
  <v-container class="narrow-container">
    <BaseDialog
      v-model="deleteDialog"
      color="error"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      @confirm="deleteNotifier(deleteTargetId)"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>
    <BaseDialog v-model="createDialog" :title="$t('events.new-notification')" @submit="createNewNotifier">
      <v-card-text>
        <v-text-field v-model="createNotifierData.name" :label="$t('general.name')"></v-text-field>
        <v-text-field v-model="createNotifierData.appriseUrl" :label="$t('events.apprise-url')"></v-text-field>
      </v-card-text>
    </BaseDialog>

    <BasePageTitle divider>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-notifiers.svg')"></v-img>
      </template>
      <template #title> {{ $t("events.event-notifiers") }} </template>
      {{ $t("events.new-notification-form-description") }}

      <div class="mt-3 d-flex flex-wrap justify-space-between mx-n2">
        <a href="https://github.com/caronc/apprise/wiki" target="_blanks" class="mx-2"> Apprise </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_gotify" target="_blanks" class="mx-2"> Gotify </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_discord" target="_blanks" class="mx-2"> Discord </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_homeassistant" target="_blanks" class="mx-2"> Home Assistant </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_matrix" target="_blanks" class="mx-2"> Matrix </a>
        <a href="https://github.com/caronc/apprise/wiki/Notify_pushover" target="_blanks" class="mx-2"> Pushover </a>
      </div>
    </BasePageTitle>

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
          <v-text-field v-model="notifiers[index].name" :label="$t('general.name')"></v-text-field>
          <v-text-field
            v-model="notifiers[index].appriseUrl"
            :label="$t('events.apprise-url-skipped-if-blank')"
          ></v-text-field>
          <v-checkbox v-model="notifiers[index].enabled" :label="$t('events.enable-notifier')" dense></v-checkbox>

          <v-divider></v-divider>
          <p class="pt-4">{{ $t("events.what-events") }}</p>
          <div class="notifier-options">
            <section v-for="sec in optionsSections" :key="sec.id">
              <h4>
                {{ sec.text }}
              </h4>
              <v-checkbox
                v-for="opt in sec.options"
                :key="opt.key"
                v-model="notifiers[index].options[opt.key]"
                hide-details
                dense
                :label="opt.text"
              />
            </section>
          </div>
          <v-card-actions class="py-0">
            <v-spacer></v-spacer>
            <BaseButtonGroup
              :buttons="[
                {
                  icon: $globals.icons.delete,
                  text: $tc('general.delete'),
                  event: 'delete',
                },
                {
                  icon: $globals.icons.testTube,
                  text: $tc('general.test'),
                  event: 'test',
                },
                {
                  icon: $globals.icons.save,
                  text: $tc('general.save'),
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
import { GroupEventNotifierCreate, GroupEventNotifierOut } from "~/lib/api/types/household";

interface OptionKey {
  text: string;
  key: keyof GroupEventNotifierOut["options"];
}


interface OptionSection {
  id: number;
  text: string;
  options: OptionKey[];
}

export default defineComponent({
  middleware: ["auth", "advanced-only"],
  setup() {
    const api = useUserApi();

    const state = reactive({
      deleteDialog: false,
      createDialog: false,
      deleteTargetId: "",
    });

    const notifiers = useAsync(async () => {
      const { data } = await api.groupEventNotifier.getAll();
      return data?.items;
    }, useAsyncKey());

    async function refreshNotifiers() {
      const { data } = await api.groupEventNotifier.getAll();
      notifiers.value = data?.items;
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

    const optionsSections: OptionSection[] = [
      {
        id: 1,
        text: i18n.tc("events.recipe-events"),
        options: [
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
        ],
      },
      {
        id: 2,
        text: i18n.tc("events.user-events"),
        options: [
          {
            text: i18n.tc("events.when-a-new-user-joins-your-group"),
            key: "userSignup",
          },
        ],
      },
      {
        id: 3,
        text: i18n.tc("events.mealplan-events"),
        options: [
          {
            text: i18n.tc("events.when-a-user-in-your-group-creates-a-new-mealplan"),
            key: "mealplanEntryCreated",
          },
        ],
      },
      {
        id: 4,
        text: i18n.tc("events.shopping-list-events"),
        options: [
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
        ],
      },
      {
        id: 5,
        text: i18n.tc("events.cookbook-events"),
        options: [
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
        ],
      },
      {
        id: 6,
        text: i18n.tc("events.tag-events"),
        options: [
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
        ],
      },
      {
        id: 7,
        text: i18n.tc("events.category-events"),
        options: [
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
        ],
      },
    ];

    return {
      ...toRefs(state),
      openDelete,
      notifiers,
      createNotifierData,
      optionsSections,
      deleteNotifier,
      testNotifier,
      saveNotifier,
      createNewNotifier,
    };
  },
  head() {
    return {
      title: this.$t("profile.notifiers"),
    };
  },
});
</script>

<style>
.notifier-options {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>
