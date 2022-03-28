<template>
  <v-container fluid class="md-container">
    <BaseCardSectionTitle title="Site Analytics">
      Your instance of Mealie can send anonymous usage statistics to the Mealie project team. This is done to help us
      gauge the usage of mealie, provide public statistics and to help us improve the user experience.

      <p class="pt-4 pb-0 mb-0">
        Your installation creates a UUID that is used to identify your installation,
        <strong> this is randomly generated using the UUID4 implementation in python</strong>. This UUID is stored on
        our analytics server and used to ensure your data is only counted once.
      </p>
    </BaseCardSectionTitle>
    <BannerExperimental />
    <section>
      <BaseCardSectionTitle class="pb-0" :icon="$globals.icons.chart" title="Analytics Settings">
      </BaseCardSectionTitle>
      <v-card outlined>
        <v-card-text>
          <v-switch v-model="state.analyticsEnabled" label="Collect Anonymous Analytics" />
        </v-card-text>
      </v-card>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive } from "@nuxtjs/composition-api";

export default defineComponent({
  layout: "admin",
  setup() {
    const state = reactive({
      analyticsEnabled: false,
    });

    return {
      state,
    };
  },
  head() {
    return {
      title: this.$t("settings.migrations") as string,
    };
  },
});
</script>

<style scoped></style>
