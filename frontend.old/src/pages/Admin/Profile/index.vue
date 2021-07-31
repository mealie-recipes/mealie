<template>
  <div class="mt-10">
    <v-row>
      <v-col cols="12" sm="12" lg="6">
        <UserCard />
        <ProfileThemeCard class="mt-10" />
        <APITokenCard class="mt-10" />
      </v-col>
      <v-col cols="12" sm="12" lg="6">
        <ProfileGroupCard />
      </v-col>
    </v-row>
    <v-row class="mt-7">
      <v-col cols="12" sm="12" lg="6"> </v-col>
      <v-col cols="12" sm="12" lg="6"> </v-col>
    </v-row>
  </div>
</template>

<script>
import ProfileThemeCard from "./ProfileThemeCard";
import ProfileGroupCard from "./ProfileGroupCard";
import APITokenCard from "./APITokenCard";
import UserCard from "./UserCard";
export default {
  components: {
    UserCard,
    ProfileThemeCard,
    ProfileGroupCard,
    APITokenCard,
  },
};
</script>

<style></style>
