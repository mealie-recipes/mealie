<template>
  <v-container v-if="statistics" class="mt-10">
    <v-row v-if="statistics">
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
      <v-col>
        <AdminEventViewer
          v-if="events"
          :events="events.events"
          :total="events.total"
          @delete-all="deleteEvents"
          @delete-item="deleteEvent"
        />
      </v-col>
    </v-row>
  </v-container>
</template>


<script lang="ts">
import { defineComponent, useAsync } from "@nuxtjs/composition-api";
import AdminEventViewer from "@/components/Domain/Admin/AdminEventViewer.vue";
import { useAdminApi, useApiSingleton } from "~/composables/use-api";
import { useAsyncKey } from "~/composables/use-utils";

export default defineComponent({
  components: { AdminEventViewer },
  layout: "admin",
  setup() {
    const api = useApiSingleton();

    const adminApi = useAdminApi();

    function getStatistics() {
      const statistics = useAsync(async () => {
        const { data } = await adminApi.about.statistics();
        return data;
      }, useAsyncKey());

      return statistics;
    }

    function getEvents() {
      const events = useAsync(async () => {
        const { data } = await api.events.getEvents();
        return data;
      }, useAsyncKey());
      return events;
    }

    async function refreshEvents() {
      const { data } = await api.events.getEvents();
      events.value = data;
    }

    async function deleteEvent(id: number) {
      const { response } = await api.events.deleteEvent(id);

      if (response && response.status === 200) {
        refreshEvents();
      }
    }

    async function deleteEvents() {
      const { response } = await api.events.deleteEvents();

      if (response && response.status === 200) {
        events.value = { events: [], total: 0 };
      }
    }

    const events = getEvents();
    const statistics = getStatistics();

    return { statistics, events, deleteEvents, deleteEvent };
  },
  head() {
    return {
      title: this.$t("sidebar.dashboard") as string,
    };
  },
});
</script>

<style scoped>
</style>