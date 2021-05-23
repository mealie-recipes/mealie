<template>
  <div>
    <v-card flat>
      <v-tabs v-model="tab" background-color="primary" centered dark icons-and-text>
        <v-tabs-slider></v-tabs-slider>

        <v-tab href="#users">
          {{ $t("user.users") }}
          <v-icon>{{ $globals.icons.user }}</v-icon>
        </v-tab>

        <v-tab href="#sign-ups">
          {{ $t("signup.sign-up-links") }}
          <v-icon>mdi-account-plus-outline</v-icon>
        </v-tab>

        <v-tab href="#groups">
          {{ $t("group.groups") }}
          <v-icon>{{ $globals.icons.group }}</v-icon>
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab">
        <v-tab-item value="users">
          <TheUserTable />
        </v-tab-item>
        <v-tab-item value="sign-ups">
          <TheSignUpTable />
        </v-tab-item>
        <v-tab-item value="groups">
          <GroupDashboard />
        </v-tab-item>
      </v-tabs-items>
    </v-card>
  </div>
</template>

<script>
import TheUserTable from "./TheUserTable";
import GroupDashboard from "./GroupDashboard";
import TheSignUpTable from "./TheSignUpTable";
export default {
  components: { TheUserTable, GroupDashboard, TheSignUpTable },
  data() {
    return {};
  },
  computed: {
    tab: {
      set(tab) {
        this.$router.replace({ query: { ...this.$route.query, tab } });
      },
      get() {
        return this.$route.query.tab;
      },
    },
  },
  mounted() {
    this.$store.dispatch("requestAllGroups");
  },
};
</script>

<style></style>
