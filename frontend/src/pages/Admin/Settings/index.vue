<template>
  <v-card>
    <v-card-title class="headline">
      {{ $t("settings.admin-settings") }}
      <v-spacer></v-spacer>
      <span>
        <v-btn class="pt-1" text href="/docs">
          {{ $t("settings.local-api") }}
          <v-icon right>mdi-open-in-new</v-icon>
        </v-btn>
      </span>
    </v-card-title>

    <v-divider></v-divider>
    <HomePageSettings />
    <v-divider></v-divider>
    <CustomPageCreator />
    <v-divider></v-divider>
  </v-card>
</template>

<script>
import HomePageSettings from "@/components/Admin/General/HomePageSettings";
import CustomPageCreator from "@/components/Admin/General/CustomPageCreator";

export default {
  components: {
    HomePageSettings,
    CustomPageCreator,
  },
};
</script>

<style>
</style>