<template>
  <v-container>
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="200" max-width="200" class="mb-2" :src="require('~/static/svgs/data-reports.svg')"></v-img>
      </template>
      <template #title> {{ $t('group.report') }} </template>
    </BasePageTitle>
    <v-container v-if="report">
      <BaseCardSectionTitle :title="report.name"> </BaseCardSectionTitle>

      <v-card-text> {{ $t('group.report-with-id', { id:id }) }} </v-card-text>

      <v-data-table :headers="itemHeaders" :items="report.entries" :items-per-page="50" show-expand>
        <template #item.success="{ item }">
          <v-icon :color="item.success ? 'success' : 'error'">
            {{ item.success ? $globals.icons.checkboxMarkedCircle : $globals.icons.close }}
          </v-icon>
        </template>
        <template #item.timestamp="{ item }">
          {{ $d(Date.parse(item.timestamp), "short") }}
        </template>
        <template #expanded-item="{ headers, item }">
          <td v-if="item.exception" class="pa-6" :colspan="headers.length">{{ item.exception }}</td>
        </template>
      </v-data-table>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useRoute, ref, onMounted } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { ReportOut } from "~/lib/api/types/reports";

export default defineComponent({
  middleware: "auth",
  setup() {
    const route = useRoute();
    const id = route.value.params.id;

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
      { text: "Success", value: "success" },
      { text: "Message", value: "message" },
      { text: "Timestamp", value: "timestamp" },
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
