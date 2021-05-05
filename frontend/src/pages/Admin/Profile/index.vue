<template>
  <div class="mt-10">
    <v-row>
      <v-col cols="12" sm="12" lg="6">
        <UserCard />
      </v-col>
      <v-col cols="12" sm="12" lg="6"> </v-col>
    </v-row>
    <v-row class="mt-7">
      <v-col cols="12" sm="12" lg="6">
        <ThemeCard />
      </v-col>
      <v-col cols="12" sm="12" lg="6"> </v-col>
    </v-row>
  </div>
</template>

<script>
import ThemeCard from "./ThemeCard";
import UserCard from "./UserCard";
export default {
  components: {
    UserCard,
    ThemeCard,
  },
};
</script>

<style></style>
