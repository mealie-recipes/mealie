<template>
  <div v-if="providerSettings">
    <BaseCardSectionTitle :title="$t('group.ai-provider-settings.ai-provider-settings')" />

    <v-row class="mb-4">
      <v-col cols="12">
        <v-autocomplete
          v-model="local.defaultProviderId"
          :label="$t('group.ai-provider-settings.default-provider')"
          :items="local.providers"
          item-title="name"
          item-value="id"
          clearable
          hide-details
          density="compact"
          variant="outlined"
        />
      </v-col>
      <v-col cols="12">
        <v-autocomplete
          v-model="local.audioProviderId"
          :label="$t('group.ai-provider-settings.audio-provider')"
          :items="local.providers"
          item-title="name"
          item-value="id"
          clearable
          hide-details
          density="compact"
          variant="outlined"
        />
      </v-col>
      <v-col cols="12">
        <v-autocomplete
          v-model="local.imageProviderId"
          :label="$t('group.ai-provider-settings.image-provider')"
          :items="local.providers"
          item-title="name"
          item-value="id"
          clearable
          hide-details
          density="compact"
          variant="outlined"
        />
      </v-col>
    </v-row>

    <BaseCardSectionTitle
      :title="$t('group.ai-provider-settings.providers')"
      size="medium"
      class="pt-2"
    >
      <template #append-title>
        <BaseButton
          :text="$t('group.ai-provider-settings.create-provider')"
          class="ms-auto my-2"
          create
          small
          @click="console.log('create (TODO)')"
        />
      </template>
    </BaseCardSectionTitle>

    <v-card
      v-for="provider in local.providers"
      :key="provider.id"
      variant="tonal"
      class="pa-0 mb-4"
    >
      <v-row no-gutters>
        <v-col :cols="10">
          <v-card-text class="">
            {{ provider.name }}
          </v-card-text>
        </v-col>

        <v-col :cols="2">
          <BaseButtonGroup
            :buttons="[

              {
                icon: $globals.icons.edit,
                text: $t('general.edit'),
                event: 'edit',
              },
              {
                icon: $globals.icons.delete,
                text: $t('general.delete'),
                event: 'delete',
              },
            ]"
            @edit="console.log(`edit ${provider.id} (TODO)`)"
            @delete="console.log(`delete ${provider.id} (TODO)`)"
          />
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import type { AIProviderSettingsOut } from "~/lib/api/types/user";

const providerSettings = defineModel<AIProviderSettingsOut>({ required: true });
const local = reactive({ ...providerSettings.value });
watch(local, (newVal) => { providerSettings.value = { ...newVal }; });
</script>
