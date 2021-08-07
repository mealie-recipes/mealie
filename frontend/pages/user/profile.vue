<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" sm="12" md="12" lg="6">
        <UserProfileCard class="mt-14" />
      </v-col>
      <v-col cols="12" sm="12" md="12" lg="6">
        <UserThemeCard class="mt-14" />
      </v-col>
    </v-row>
  </v-container>
</template>
    
    <script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import UserProfileCard from "~/components/Domain/User/UserProfileCard.vue";
import UserThemeCard from "~/components/Domain/User/UserThemeCard.vue";

export default defineComponent({
  components: { UserProfileCard, UserThemeCard },
  layout: "admin",
  setup() {
    return {};
  },
});
</script>
    
    <style scoped>
</style>