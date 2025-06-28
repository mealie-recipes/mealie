<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img
          width="100%"
          max-height="125"
          max-width="125"
          :src="require('~/static/svgs/manage-webhooks.svg')"
        />
      </template>
      <template #title>
        {{ $t('settings.webhooks.webhooks') }}
      </template>
      <v-card-text class="pb-0">
        {{ $t('settings.webhooks.description') }}
      </v-card-text>
    </BasePageTitle>

    <BaseButton
      create
      @click="actions.createOne()"
    />
    <v-expansion-panels class="mt-2">
      <v-expansion-panel
        v-for="(webhook, index) in webhooks"
        :key="index"
        class="my-2 left-border rounded"
      >
        <v-expansion-panel-title
          disable-icon-rotate
          class="headline"
        >
          <div class="d-flex align-center">
            <v-icon
              size="large"
              start
              :color="webhook.enabled ? 'info' : undefined"
            >
              {{ $globals.icons.webhook }}
            </v-icon>
            {{ webhook.name }} - {{ $d(timeUTC(webhook.scheduledTime), "time") }}
          </div>
          <template #actions>
            <v-btn
              size="small"
              icon
              flat
              class="ml-2"
            >
              <v-icon>
                {{ $globals.icons.edit }}
              </v-icon>
            </v-btn>
          </template>
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <GroupWebhookEditor
            :key="webhook.id"
            :webhook="webhook"
            @save="actions.updateOne($event)"
            @delete="actions.deleteOne($event)"
            @test="actions.testOne($event).then(() => alert.success($t('events.test-message-sent')))"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script lang="ts">
import { useGroupWebhooks, timeUTC } from "~/composables/use-group-webhooks";
import GroupWebhookEditor from "~/components/Domain/Household/GroupWebhookEditor.vue";
import { alert } from "~/composables/use-toast";

export default defineNuxtComponent({
  components: { GroupWebhookEditor },
  middleware: ["sidebase-auth", "advanced-only"],
  setup() {
    const i18n = useI18n();
    const { actions, webhooks } = useGroupWebhooks();

    useSeoMeta({
      title: i18n.t("settings.webhooks.webhooks"),
    });

    return {
      alert,
      webhooks,
      actions,
      timeUTC,
    };
  },
});
</script>
