<template>
  <div>
    <v-card-text>
      <v-switch v-model="webhookCopy.enabled" label="Enabled"></v-switch>
      <v-text-field v-model="webhookCopy.name" label="Webhook Name"></v-text-field>
      <v-text-field v-model="webhookCopy.url" label="Webhook Url"></v-text-field>
      <v-time-picker v-model="scheduledTime" class="elevation-2" ampm-in-title format="ampm"></v-time-picker>
    </v-card-text>
    <v-card-actions class="py-0 justify-end">
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
        @delete="$emit('delete', webhookCopy.id)"
        @save="handleSave"
        @test="$emit('test', webhookCopy.id)"
      />
    </v-card-actions>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from "@nuxtjs/composition-api";
import { ReadWebhook } from "~/types/api-types/group";
import { timeLocalToUTC, timeUTCToLocal } from "~/composables/use-group-webhooks";

export default defineComponent({
  props: {
    webhook: {
      type: Object as () => ReadWebhook,
      required: true,
    },
  },
  emits: ["delete", "save", "test"],
  setup(props, { emit }) {
    const itemUTC = ref(props.webhook.scheduledTime);
    const itemLocal = ref(timeUTCToLocal(props.webhook.scheduledTime));

    const scheduledTime = computed({
      get() {
        return itemLocal.value;
      },
      set(v) {
        itemUTC.value = timeLocalToUTC(v);
        itemLocal.value = v;
      },
    });

    const webhookCopy = ref({ ...props.webhook });

    function handleSave() {
      webhookCopy.value.scheduledTime = itemLocal.value;
      emit("save", webhookCopy.value);
    }

    return {
      webhookCopy,
      scheduledTime,
      handleSave,
      itemUTC,
      itemLocal,
    };
  },
  head() {
    return {
      title: this.$tc("settings.webhooks.webhooks"),
    };
  },
});
</script>
