<template>
  <div class="mt-10">
    <v-row>
      <v-col cols="12" sm="12" md="4">
        <StatCard icon="mdi-silverware-fork-knife">
          <template v-slot:after-heading>
            <div class="ml-auto text-right">
              <div class="body-3 grey--text font-weight-light" v-text="'Recipes'" />

              <h3 class="display-2 font-weight-light text--primary">
                <small> {{ statistics.totalRecipes }}</small>
              </h3>
            </div>
          </template>
          <template v-slot:actions>
            <div class="d-flex row py-3 justify-space-around">
              <v-btn small color="primary" :to="{ path: '/admin/toolbox/', query: { tab: 'organize', filter: 'tag' } }">
                <v-icon left> mdi-tag </v-icon> Untagged {{ statistics.untaggedRecipes }}
              </v-btn>
              <v-btn
                small
                color="primary"
                :to="{ path: '/admin/toolbox/', query: { tab: 'organize', filter: 'category' } }"
              >
                <v-icon left> mdi-tag </v-icon> Uncategorized {{ statistics.uncategorizedRecipes }}
              </v-btn>
            </div>
          </template>
        </StatCard>
      </v-col>
      <v-col cols="12" sm="12" md="4">
        <StatCard icon="mdi-account">
          <template v-slot:after-heading>
            <div class="ml-auto text-right">
              <div class="body-3 grey--text font-weight-light" v-text="'Users'" />

              <h3 class="display-2 font-weight-light text--primary">
                <small> {{ statistics.totalUsers }}</small>
              </h3>
            </div>
          </template>
          <template v-slot:actions>
            <div class="ml-auto">
              <v-btn color="primary" small to="/admin/manage-users?tab=users">
                <v-icon left>mdi-account</v-icon>
                Manage Users
              </v-btn>
            </div>
          </template>
        </StatCard>
      </v-col>
      <v-col cols="12" sm="12" md="4">
        <StatCard icon="mdi-account-group">
          <template v-slot:after-heading>
            <div class="ml-auto text-right">
              <div class="body-3 grey--text font-weight-light" v-text="'Groups'" />

              <h3 class="display-2 font-weight-light text--primary">
                <small> {{ statistics.totalGroups }}</small>
              </h3>
            </div>
          </template>
          <template v-slot:actions>
            <div class="ml-auto">
              <v-btn color="primary" small to="/admin/manage-users?tab=groups">
                <v-icon left>mdi-account-group</v-icon>
                Manage Groups
              </v-btn>
            </div>
          </template>
        </StatCard>
      </v-col>
    </v-row>
    <v-row class="mt-10">
      <v-col cols="12" sm="12" lg="6">
        <EventViewer />
      </v-col>
      <v-col cols="12" sm="12" lg="6"> <BackupViewer /> </v-col>
    </v-row>
  </div>
</template>

<script>
import { api } from "@/api";
import StatCard from "./StatCard";
import EventViewer from "./EventViewer";
import BackupViewer from "./BackupViewer";
export default {
  components: { StatCard, EventViewer, BackupViewer },
  data() {
    return {
      statistics: {
        totalGroups: 0,
        totalRecipes: 0,
        totalUsers: 0,
        uncategorizedRecipes: 0,
        untaggedRecipes: 0,
      },
    };
  },
  mounted() {
    this.getStatistics();
  },
  methods: {
    async getStatistics() {
      this.statistics = await api.meta.getStatistics();
    },
  },
};
</script>

<style>
.grid-style {
  flex-grow: inherit;
  display: inline-flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>