<template>
  <v-container
    fluid
    class="narrow-container"
  >
    <BasePageTitle divider>
      <template #header>
        <v-icon size="48">
          {{ $globals.icons.lock }}
        </v-icon>
      </template>
      <template #title>
        {{ $t("legal.privacy-policy") }}
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
        {{ $t("legal.data-controller") }}
      </h2>
      <p>
        {{ controllerName || $t("legal.to-be-completed") }}
        <template v-if="contactEmail">
          — <a :href="`mailto:${contactEmail}`">{{ contactEmail }}</a>
        </template>
      </p>

      <h2 class="text-h6 mt-6 mb-2">
        {{ $t("legal.data-collected") }}
      </h2>
      <p>{{ $t("legal.data-collected-description") }}</p>
      <ul class="mb-2">
        <li>{{ $t("legal.data-account") }}</li>
        <li>{{ $t("legal.data-content") }}</li>
        <li>{{ $t("legal.data-technical") }}</li>
      </ul>

      <h2 class="text-h6 mt-6 mb-2">
        {{ $t("legal.purpose") }}
      </h2>
      <p>{{ $t("legal.purpose-description") }}</p>

      <h2 class="text-h6 mt-6 mb-2">
        {{ $t("legal.legal-basis") }}
      </h2>
      <p>{{ $t("legal.legal-basis-description") }}</p>

      <h2 class="text-h6 mt-6 mb-2">
        {{ $t("legal.retention") }}
      </h2>
      <p>{{ $t("legal.retention-description") }}</p>

      <h2 class="text-h6 mt-6 mb-2">
        {{ $t("legal.third-parties") }}
      </h2>
      <p>{{ $t("legal.third-parties-description") }}</p>

      <h2 class="text-h6 mt-6 mb-2">
        {{ $t("legal.security") }}
      </h2>
      <p>{{ $t("legal.security-description") }}</p>

      <h2 class="text-h6 mt-6 mb-2">
        {{ $t("legal.your-rights") }}
      </h2>
      <p>{{ $t("legal.your-rights-description") }}</p>
      <ul class="mb-2">
        <li>{{ $t("legal.right-access") }}</li>
        <li>{{ $t("legal.right-rectification") }}</li>
        <li>
          {{ $t("legal.right-erasure") }}
          <i18n-t
            keypath="legal.right-erasure-self-service"
            tag="span"
          >
            <template #link>
              <nuxt-link to="/user/profile/edit">
                {{ $t("legal.right-erasure-self-service-link") }}
              </nuxt-link>
            </template>
          </i18n-t>
        </li>
        <li>{{ $t("legal.right-portability") }}</li>
      </ul>
      <p>
        {{ $t("legal.rights-contact") }}
        <a
          v-if="contactEmail"
          :href="`mailto:${contactEmail}`"
        >{{ contactEmail }}</a>
        <template v-else>
          {{ $t("legal.to-be-completed") }}
        </template>.
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
  title: i18n.t("legal.privacy-policy"),
});

const controllerName = computed(() => $appInfo.legalControllerName);
const contactEmail = computed(() => $appInfo.legalContactEmail);
</script>
