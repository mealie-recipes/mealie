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
          Users
          <v-icon>mdi-account</v-icon>
        </v-tab>

        <v-tab>
          Sign-Up Links
          <v-icon>mdi-account-plus-outline</v-icon>
        </v-tab>

        <v-tab>
          Groups
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
import TheUserTable from "@/components/Admin/ManageUsers/TheUserTable";
import GroupDashboard from "@/components/Admin/ManageUsers/GroupDashboard";
import TheSignUpTable from "@/components/Admin/ManageUsers/TheSignUpTable";
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