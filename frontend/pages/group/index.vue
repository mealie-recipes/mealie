<template>
  <v-container class="narrow-container">
    <BasePageTitle class="mb-5">
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-group-settings.svg')"></v-img>
      </template>
      <template #title> {{ $t("profile.group-settings") }} </template>
      {{ $t("profile.group-description") }}
    </BasePageTitle>

    <section v-if="group">
      <BaseCardSectionTitle class="mt-10" :title="$tc('group.group-preferences')"></BaseCardSectionTitle>
      <div class="mb-6">
        <v-checkbox
          v-model="group.preferences.privateGroup"
          hide-details
          dense
          :label="$t('group.private-group')"
          @change="groupActions.updatePreferences()"
        />
        <div class="ml-8">
          <p class="text-subtitle-2 my-0 py-0">
            {{ $t("group.private-group-description") }}
          </p>
          <DocLink class="mt-2" link="/documentation/getting-started/faq/#how-do-private-groups-and-recipes-work" />
        </div>
      </div>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { useGroupSelf } from "~/composables/use-groups";

export default defineComponent({
  middleware: ["auth", "can-manage-only"],
  setup() {
    const { group, actions: groupActions } = useGroupSelf();

    return {
      group,
      groupActions,
    };
  },
  head() {
    return {
      title: this.$t("group.group") as string,
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
