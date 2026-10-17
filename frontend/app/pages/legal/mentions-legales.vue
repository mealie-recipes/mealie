<template>
  <v-container
    fluid
    class="narrow-container"
  >
    <BasePageTitle divider>
      <template #header>
        <v-icon size="48">
          {{ $globals.icons.informationOutline }}
        </v-icon>
      </template>
      <template #title>
        {{ $t("legal.legal-notice") }}
      </template>
    </BasePageTitle>

    <v-card-text class="text-body-1">
      <v-alert
        v-if="!controllerName || !contactEmail"
        type="warning"
        variant="outlined"
        class="mb-6"
      >
        {{ $t("legal.not-configured-warning") }}
      </v-alert>

      <h2 class="text-h6 mt-4 mb-2">
        {{ $t("legal.publisher") }}
      </h2>
      <p>{{ controllerName || $t("legal.to-be-completed") }}</p>

      <h2 class="text-h6 mt-6 mb-2">
        {{ $t("legal.contact") }}
      </h2>
      <p>
        <a
          v-if="contactEmail"
          :href="`mailto:${contactEmail}`"
        >{{ contactEmail }}</a>
        <template v-else>
          {{ $t("legal.to-be-completed") }}
        </template>
      </p>

      <h2 class="text-h6 mt-6 mb-2">
        {{ $t("legal.hosting") }}
      </h2>
      <p>{{ $t("legal.hosting-description") }}</p>

      <h2 class="text-h6 mt-6 mb-2">
        {{ $t("legal.source-code") }}
      </h2>
      <p>
        {{ $t("legal.source-code-description") }}
        <a
          :href="sourceUrl"
          target="_blank"
          rel="noopener"
        >{{ sourceUrl }}</a>
      </p>
    </v-card-text>
  </v-container>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "blank",
});

const i18n = useI18n();
const { $appInfo } = useNuxtApp();

useSeoMeta({
  title: i18n.t("legal.legal-notice"),
});

const controllerName = computed(() => $appInfo.legalControllerName);
const contactEmail = computed(() => $appInfo.legalContactEmail);
const sourceUrl = computed(() => $appInfo.legalSourceUrl);
</script>
