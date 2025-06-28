<template>
  <v-container>
    <BasePageTitle divider>
      <template #header>
        <v-img
          width="100%"
          max-height="200"
          max-width="200"
          class="mb-2"
          :src="require('~/static/svgs/data-reports.svg')"
        />
      </template>
      <template #title>
        {{ $t('group.report') }}
      </template>
    </BasePageTitle>
    <v-container v-if="report">
      <BaseCardSectionTitle :title="report.name" />

      <v-card-text> {{ $t('group.report-with-id', { id: id }) }} </v-card-text>

      <v-data-table
        :headers="itemHeaders"
        :items="report.entries"
        :items-per-page="50"
        show-expand
      >
        <template #[`item.success`]="{ item }">
          <v-icon :color="item.success ? 'success' : 'error'">
            {{ item.success ? $globals.icons.checkboxMarkedCircle : $globals.icons.close }}
          </v-icon>
        </template>
        <template #[`item.timestamp`]="{ item }">
          {{ $d(Date.parse(item.timestamp!), "short") }}
        </template>
        <template #[`expanded-item`]="{ headers, item }">
          <td
            v-if="item.exception"
            class="pa-6"
            :colspan="headers.length"
          >
            {{ item.exception }}
          </td>
        </template>
      </v-data-table>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import type { ReportOut } from "~/lib/api/types/reports";

export default defineNuxtComponent({
  middleware: "sidebase-auth",
  setup() {
    const route = useRoute();
    const id = route.params.id as string;

    const api = useUserApi();

    const report = ref<ReportOut | null>(null);

    async function getReport() {
      const { data } = await api.groupReports.getOne(id);
      report.value = data ?? null;
    }

    onMounted(async () => {
      await getReport();
    });

    const itemHeaders = [
      { title: "Success", value: "success" },
      { title: "Message", value: "message" },
      { title: "Timestamp", value: "timestamp" },
    ];

    return {
      report,
      id,
      itemHeaders,
    };
  },
});
</script>

<style lang="scss" scoped></style>
