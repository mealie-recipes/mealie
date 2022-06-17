<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-webhooks.svg')"></v-img>
      </template>
      <template #title> Webhooks </template>
      <v-card-text class="pb-0">
        The webhooks defined below will be executed when a meal is defined for the day. At the scheduled time the
        webhooks will be sent with the data from the recipe that is scheduled for the day. Note that webhook execution
        is not exact. The webhooks are executed on a 5 minutes interval so the webhooks will be executed within 5 +/-
        minutes of the scheduled.
      </v-card-text>
    </BasePageTitle>

    <BannerExperimental />

    <BaseButton create @click="actions.createOne()" />
    <v-expansion-panels class="mt-2">
      <v-expansion-panel v-for="(webhook, index) in webhooks" :key="index" class="my-2 left-border rounded">
        <v-expansion-panel-header disable-icon-rotate class="headline">
          <div class="d-flex align-center">
            <v-icon large left :color="webhook.enabled ? 'info' : null">
              {{ $globals.icons.webhook }}
            </v-icon>
            {{ webhook.name }} - {{ timeDisplay(timeUTCToLocal(webhook.scheduledTime)) }}
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
          />
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { useGroupWebhooks, timeLocalToUTC, timeUTCToLocal } from "~/composables/use-group-webhooks";
import GroupWebhookEditor from "~/components/Domain/Group/GroupWebhookEditor.vue";

export default defineComponent({
  components: { GroupWebhookEditor },
  setup() {
    const { actions, webhooks } = useGroupWebhooks();
    function timeDisplay(time: string): string {
      // returns the time in the format HH:MM AM/PM
      const [hours, minutes] = time.split(":");
      const ampm = Number(hours) < 12 ? "AM" : "PM";
      const hour = Number(hours) % 12 || 12;
      const minute = minutes.padStart(2, "0");
      return `${hour}:${minute} ${ampm}`;
    }

    return {
      webhooks,
      actions,
      timeLocalToUTC,
      timeUTCToLocal,
      timeDisplay,
    };
  },
  head() {
    return {
      title: this.$t("settings.webhooks.webhooks") as string,
    };
  },
});
</script>
