<template>
  <v-menu location="bottom end" :offset="8" :close-on-content-click="false" max-width="380">
    <template #activator="{ props }">
      <v-btn
        v-bind="props"
        :icon="mdiHelpCircleOutline"
        :aria-label="$t('search.syntax-help')"
        :title="$t('search.syntax-help')"
        size="small"
        variant="text"
        @keydown.stop
      />
    </template>
    <v-card rounded="lg" @keydown.stop>
      <v-card-text class="text-body-2">
        <p class="font-weight-medium mb-3">
          {{ $t("search.syntax-help") }}
        </p>
        <p>{{ $t("search.syntax-description") }}</p>
        <p class="text-medium-emphasis mt-3">
          {{ $t("search.exclusion-description") }}
        </p>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script setup lang="ts">
import { mdiHelpCircleOutline } from "@mdi/js";
</script>
