<template>
  <v-container>
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-group-settings.svg')"></v-img>
      </template>
      <template #title> Group Settings </template>
      These items are shared within your group. Editing one of them will change it for the whole group!
    </BasePageTitle>
    <v-card tag="section" outlined>
      <v-card-text>
        <BaseCardSectionTitle title="Mealplan Categories">
          Set the categories below for the ones that you want to be included in your mealplan random generation.
          <div class="mt-2">
            <BaseButton save @click="actions.updateAll()" />
          </div>
        </BaseCardSectionTitle>
        <DomainRecipeCategoryTagSelector v-if="categories" v-model="categories" />
      </v-card-text>
    </v-card>
    <v-card tag="section" outlined class="my-7">
      <v-card-text>
        <BaseCardSectionTitle title="Mealplan Webhook">
          The webhooks defined below will be executed when a meal is defined for the day. At the scheduled time the
          webhooks will be sent with the data from the recipe that is scheduled for the day
          <div class="mt-2">
            <BaseButton create @click="webhookActions.createOne()" />
          </div>
        </BaseCardSectionTitle>
        <v-expansion-panels class="mt-2">
          <v-expansion-panel v-for="(webhook, index) in webhooks" :key="index" class="my-2 my-border rounded">
            <v-expansion-panel-header disable-icon-rotate class="headline">
              <div class="d-flex align-center">
                <v-icon large left :color="webhook.enabled ? 'info' : null">
                  {{ $globals.icons.webhook }}
                </v-icon>
                {{ webhook.name }} - {{ webhook.time }}
              </div>
              <template #actions>
                <v-btn color="info" fab small class="ml-2">
                  <v-icon color="white">
                    {{ $globals.icons.edit }}
                  </v-icon>
                </v-btn>
              </template>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-card-text>
                <v-switch v-model="webhook.enabled" label="Enabled"></v-switch>
                <v-text-field v-model="webhook.name" label="Webhook Name"></v-text-field>
                <v-text-field v-model="webhook.url" label="Webhook Url"></v-text-field>
                <v-time-picker v-model="webhook.time" class="elevation-2" ampm-in-title format="ampm"></v-time-picker>
              </v-card-text>
              <v-card-actions>
                <BaseButton secondary color="info">
                  <template #icon>
                    {{ $globals.icons.testTube }}
                  </template>
                  Test
                </BaseButton>
                <v-spacer></v-spacer>
                <BaseButton delete @click="webhookActions.deleteOne(webhook.id)" />
                <BaseButton save @click="webhookActions.updateOne(webhook)" />
              </v-card-actions>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card-text>
    </v-card>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { useGroupWebhooks } from "~/composables/use-group-webhooks";
import { useGroup } from "~/composables/use-groups";

export default defineComponent({
  setup() {
    const { categories, actions } = useGroup();
    const { actions: webhookActions, webhooks } = useGroupWebhooks();

    return {
      categories,
      actions,
      webhooks,
      webhookActions,
    };
  },
});
</script>
    
