<template>
  <v-container class="mt-10">
    <v-row>
      <v-col cols="12" sm="12" md="4">
        <BaseStatCard :icon="$globals.icons.primary">
          <template #after-heading>
            <div class="ml-auto text-right">
              <h2 class="body-3 grey--text font-weight-light">
                {{ $t("general.recipes") }}
              </h2>

              <h3 class="display-2 font-weight-light text--primary">
                <small> {{ statistics.totalRecipes }}</small>
              </h3>
            </div>
          </template>
          <template #actions>
            <div class="d-flex row py-2 justify-end">
              <v-btn class="ma-1" small color="primary" to="/admin/toolbox/organize">
                <v-icon left> {{ $globals.icons.tags }} </v-icon>
                {{ $tc("tag.untagged-count", [statistics.untaggedRecipes]) }}
              </v-btn>
              <v-btn class="ma-1" small color="primary" to="/admin/toolbox/organize">
                <v-icon left> {{ $globals.icons.tags }} </v-icon>
                {{ $tc("category.uncategorized-count", [statistics.uncategorizedRecipes]) }}
              </v-btn>
            </div>
          </template>
        </BaseStatCard>
      </v-col>
      <v-col cols="12" sm="12" md="4">
        <BaseStatCard :icon="$globals.icons.user">
          <template #after-heading>
            <div class="ml-auto text-right">
              <h2 class="body-3 grey--text font-weight-light">
                {{ $t("user.users") }}
              </h2>
              <h3 class="display-2 font-weight-light text--primary">
                <small> {{ statistics.totalUsers }}</small>
              </h3>
            </div>
          </template>
          <template #actions>
            <div class="ml-auto">
              <v-btn color="primary" small to="/admin/manage-users/all-users">
                <v-icon left>{{ $globals.icons.user }}</v-icon>
                {{ $t("user.manage-users") }}
              </v-btn>
            </div>
          </template>
        </BaseStatCard>
      </v-col>
      <v-col cols="12" sm="12" md="4">
        <BaseStatCard :icon="$globals.icons.group">
          <template #after-heading>
            <div class="ml-auto text-right">
              <h2 class="body-3 grey--text font-weight-light">
                {{ $t("group.groups") }}
              </h2>

              <h3 class="display-2 font-weight-light text--primary">
                <small> {{ statistics.totalGroups }}</small>
              </h3>
            </div>
          </template>
          <template #actions>
            <div class="ml-auto">
              <v-btn color="primary" small to="/admin/manage-users/all-groups">
                <v-icon left>{{ $globals.icons.group }}</v-icon>
                {{ $t("group.manage-groups") }}
              </v-btn>
            </div>
          </template>
        </BaseStatCard>
      </v-col>
    </v-row>
    <v-row class="mt-10" align-content="stretch">
      <v-col cols="12" sm="12" lg="6">
        <AdminEventViewer />
      </v-col>
      <v-col cols="12" sm="12" lg="6">
        <AdminBackupViewer />
      </v-col>
    </v-row>
  </v-container>
</template>


<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import AdminEventViewer from "@/components/Domain/Admin/AdminEventViewer.vue";
import AdminBackupViewer from "@/components/Domain/Admin/AdminBackupViewer.vue";

export default defineComponent({
  components: { AdminEventViewer, AdminBackupViewer },
  layout: "admin",
  setup() {
    return {};
  },
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
});
</script>

<style scoped>
</style>