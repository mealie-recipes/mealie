<template>
  <div>
    <v-card-text>
      <v-switch
        v-model="webhookCopy.enabled"
        color="primary"
        :label="$t('general.enabled')"
      />
      <v-text-field
        v-model="webhookCopy.name"
        :label="$t('settings.webhooks.webhook-name')"
        variant="underlined"
      />
      <v-text-field
        v-model="webhookCopy.url"
        :label="$t('settings.webhooks.webhook-url')"
        variant="underlined"
      />
      <v-time-picker
        v-model="scheduledTime"
        class="elevation-2"
        ampm-in-title
        format="ampm"
      />
    </v-card-text>
    <v-card-actions class="py-0 justify-end">
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
        @delete="$emit('delete', webhookCopy.id)"
        @save="handleSave"
        @test="$emit('test', webhookCopy.id)"
      />
    </v-card-actions>
  </div>
</template>

<script lang="ts">
import type { ReadWebhook } from "~/lib/api/types/household";
import { timeLocalToUTC, timeUTCToLocal } from "~/composables/use-group-webhooks";

export default defineNuxtComponent({
  props: {
    webhook: {
      type: Object as () => ReadWebhook,
      required: true,
    },
  },
  emits: ["delete", "save", "test"],
  setup(props, { emit }) {
    const i18n = useI18n();
    const itemUTC = ref<string>(props.webhook.scheduledTime);
    const itemLocal = ref<string>(timeUTCToLocal(props.webhook.scheduledTime));

    const scheduledTime = computed({
      get() {
        return itemLocal.value;
      },
      set(v: string) {
        itemUTC.value = timeLocalToUTC(v);
        itemLocal.value = v;
      },
    });

    const webhookCopy = ref({ ...props.webhook });

    function handleSave() {
      webhookCopy.value.scheduledTime = itemLocal.value;
      emit("save", webhookCopy.value);
    }

    // Set page title using useSeoMeta
    useSeoMeta({
      title: i18n.t("settings.webhooks.webhooks"),
    });

    return {
      webhookCopy,
      scheduledTime,
      handleSave,
      itemUTC,
      itemLocal,
    };
  },
});
</script>
