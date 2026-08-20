<template>
  <v-container fluid>
    <BasePageTitle>
      <template #title>
        {{ $t("user.login-history") }}
      </template>
      {{ $t("profile.user-login-history-description") }}
    </BasePageTitle>

    <UserLoginHistoryTable />
  </v-container>
</template>

<script setup lang="ts">
const i18n = useI18n();

useHead({
  title: i18n.t("user.login-history"),
});
</script>
