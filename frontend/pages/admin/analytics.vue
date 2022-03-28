<template>
  <v-container fluid class="md-container">
    <BannerExperimental></BannerExperimental>
    <BaseCardSectionTitle title="Site Analytics">
      Your instance of Mealie can send anonymous usage statistics to the Mealie project team. This is done to help us
      gauge the usage of mealie, provide public statistics and to help us improve the user experience.

      <p class="pt-4 pb-0 mb-0">
        Your installation creates a UUID that is used to identify your installation,
        <strong> this is randomly generated using the UUID4 implementation in python</strong>. This UUID is stored on
        our analytics server and used to ensure your data is only counted once.
      </p>
    </BaseCardSectionTitle>
    <section>
      <BaseCardSectionTitle class="pb-0" :icon="$globals.icons.chart" title="Analytics Settings">
        When you opt into analytics your install will register itself with the Analytics API to count the installation
        and register your generated anonymous installation ID
      </BaseCardSectionTitle>
      <v-card-text>
        <v-switch v-model="state.analyticsEnabled" label="Collect Anonymous Analytics" />
      </v-card-text>
    </section>
    <section class="my-8">
      <BaseCardSectionTitle class="pb-0" :icon="$globals.icons.chart" title="Analytics Data">
        This is a list of all the data that is sent to the Mealie project team.
      </BaseCardSectionTitle>
      <v-card class="ma-2">
        <template v-for="(value, idx) in data">
          <v-list-item :key="`item-${idx}`">
            <v-list-item-title class="py-2">
              <div>{{ value.text }}</div>
              <v-list-item-subtitle class="text-end"> {{ getValue(value.valueKey) }} </v-list-item-subtitle>
            </v-list-item-title>
          </v-list-item>
          <v-divider :key="`divider-${idx}`" class="mx-2"></v-divider>
        </template>
      </v-card>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, useAsync } from "@nuxtjs/composition-api";
import { useAdminApi } from "~/composables/api";
import { useAsyncKey } from "~/composables/use-utils";
import { MealieAnalytics } from "~/types/api-types/analytics";

type DisplayData = {
  text: string;
  valueKey: keyof MealieAnalytics;
};

export default defineComponent({
  layout: "admin",
  setup() {
    const adminApi = useAdminApi();

    const state = reactive({
      analyticsEnabled: false,
    });

    const analyticsData = useAsync(async () => {
      const { data } = await adminApi.analytics.getAnalytics();
      return data;
    }, useAsyncKey());

    function getValue(key: keyof MealieAnalytics) {
      if (!analyticsData.value) {
        return "";
      }

      return analyticsData.value[key];
    }

    const data: DisplayData[] = [
      {
        text: "Installation Id",
        valueKey: "installationId",
      },
      {
        text: "Version",
        valueKey: "version",
      },
      {
        text: "Database",
        valueKey: "databaseType",
      },
      {
        text: "Using Email",
        valueKey: "usingEmail",
      },
      {
        text: "Using LDAP",
        valueKey: "usingLdap",
      },
      {
        text: "API Tokens",
        valueKey: "apiTokens",
      },
      {
        text: "Total Users",
        valueKey: "users",
      },
      {
        text: "Total Recipes",
        valueKey: "recipes",
      },
      {
        text: "Total Groups",
        valueKey: "groups",
      },
      {
        text: "Shopping Lists",
        valueKey: "shoppingLists",
      },
      {
        text: "Cookbooks",
        valueKey: "cookbooks",
      },
    ];

    return {
      data,
      state,
      analyticsData,
      getValue,
    };
  },
  head() {
    return {
      title: "Analytics",
    };
  },
});
</script>

<style scoped></style>
