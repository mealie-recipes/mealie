<template>
  <v-container class="narrow-container">
    <BasePageTitle class="mb-5">
      <template #header>
        <v-img
          width="100%"
          max-height="100"
          max-width="100"
          :src="require('~/static/svgs/manage-group-settings.svg')"
        />
      </template>
      <template #title>
        {{ $t("profile.group-settings") }}
      </template>
      {{ $t("profile.group-description") }}
    </BasePageTitle>

    <section v-if="group">
      <BaseCardSectionTitle
        class="mt-10"
        :title="$t('group.group-preferences')"
      />
      <div class="mb-6">
        <v-checkbox
          v-model="group.preferences.privateGroup"
          hide-details
          density="compact"
          color="primary"
          :label="$t('group.private-group')"
          @change="groupActions.updatePreferences()"
        />
        <div class="ml-8">
          <p class="text-subtitle-2 my-0 py-0">
            {{ $t("group.private-group-description") }}
          </p>
          <DocLink
            class="mt-2"
            link="/documentation/getting-started/faq/#how-do-private-groups-and-recipes-work"
          />
        </div>
      </div>
    </section>
  </v-container>
</template>

<script lang="ts">
import { useGroupSelf } from "~/composables/use-groups";

export default defineNuxtComponent({
  middleware: ["sidebase-auth", "can-manage-only"],
  setup() {
    const { group, actions: groupActions } = useGroupSelf();
    const i18n = useI18n();

    useSeoMeta({
      title: i18n.t("group.group"),
    });

    return {
      group,
      groupActions,
    };
  },
});
</script>

<style lang="css">
.preference-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 600px;
}
</style>
