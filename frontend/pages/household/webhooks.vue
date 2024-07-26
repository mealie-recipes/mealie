<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-webhooks.svg')"></v-img>
      </template>
      <template #title> {{ $t('settings.webhooks.webhooks') }} </template>
      <v-card-text class="pb-0">
        {{ $t('settings.webhooks.description') }}
      </v-card-text>
    </BasePageTitle>

    <BaseButton create @click="actions.createOne()" />
    <v-expansion-panels class="mt-2">
      <v-expansion-panel v-for="(webhook, index) in webhooks" :key="index" class="my-2 left-border rounded">
        <v-expansion-panel-header disable-icon-rotate class="headline">
          <div class="d-flex align-center">
            <v-icon large left :color="webhook.enabled ? 'info' : null">
              {{ $globals.icons.webhook }}
            </v-icon>
            {{ webhook.name }} - {{ $d(timeUTC(webhook.scheduledTime), "time") }}
          </div>
          <template #actions>
            <v-btn small icon class="ml-2">
              <v-icon>
                {{ $globals.icons.edit }}
              </v-icon>
            </v-btn>
          </template>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <GroupWebhookEditor
            :key="webhook.id"
            :webhook="webhook"
            @save="actions.updateOne($event)"
            @delete="actions.deleteOne($event)"
            @test="actions.testOne($event).then(() => alert.success($tc('events.test-message-sent')))"
          />
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { useGroupWebhooks, timeUTC } from "~/composables/use-group-webhooks";
import GroupWebhookEditor from "~/components/Domain/Household/GroupWebhookEditor.vue";
import { alert } from "~/composables/use-toast";

export default defineComponent({
  components: { GroupWebhookEditor },
  middleware: ["auth", "advanced-only"],
  setup() {
    const { actions, webhooks } = useGroupWebhooks();

    return {
      alert,
      webhooks,
      actions,
      timeUTC
    };
  },
  head() {
    return {
      title: this.$t("settings.webhooks.webhooks") as string,
    };
  },
});
</script>
