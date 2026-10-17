<template>
  <v-footer
    color="primary"
    padless
    app
  >
    <v-row
      justify="center"
      align="center"
      density="comfortable"
      no-gutters
    >
      <v-col
        class="py-2 text-center white--text"
        cols="12"
      >
        <v-btn
          color="white"
          icon
          :href="$appInfo.legalSourceUrl"
          target="_blank"
          :aria-label="$t('legal.source-code')"
        >
          <v-icon>
            {{ $globals.icons.github }}
          </v-icon>
        </v-btn>
        {{ new Date().getFullYear() }} — <strong> Mealie </strong>
        <span class="mx-2">·</span>
        <nuxt-link
          class="text-white"
          to="/legal/mentions-legales"
        >
          {{ $t('legal.legal-notice') }}
        </nuxt-link>
        <span class="mx-2">·</span>
        <nuxt-link
          class="text-white"
          to="/legal/confidentialite"
        >
          {{ $t('legal.privacy-policy') }}
        </nuxt-link>
      </v-col>
    </v-row>
  </v-footer>
</template>
