<template>
  <div>
    <v-card flat>
      <v-tabs
        v-model="tab"
        background-color="primary"
        centered
        dark
        icons-and-text
      >
        <v-tabs-slider></v-tabs-slider>

        <v-tab>
          {{ $t("user.users") }}
          <v-icon>mdi-account</v-icon>
        </v-tab>

        <v-tab>
          {{ $t("signup.sign-up-links") }}
          <v-icon>mdi-account-plus-outline</v-icon>
        </v-tab>

        <v-tab>
          {{ $t("group.groups") }}
          <v-icon>mdi-account-group</v-icon>
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab">
        <v-tab-item>
          <TheUserTable />
        </v-tab-item>
        <v-tab-item>
          <TheSignUpTable />
        </v-tab-item>
        <v-tab-item>
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
    return {
      tab: 0,
    };
  },
  mounted() {
    this.$store.dispatch("requestAllGroups");
  },
};
</script>

<style>
</style>