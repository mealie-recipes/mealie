<template>
  <v-data-table
    :headers="headers"
    :items="items"
    item-key="id"
    class="elevation-0"
    :items-per-page="50"
    @click:row="($event, { item }) => handleRowClick(item)"
  >
    <template #[`item.category`]="{ item }">
      {{ capitalize(item.category) }}
    </template>
    <template #[`item.timestamp`]="{ item }">
      {{ $d(Date.parse(item.timestamp!), "long") }}
    </template>
    <template #[`item.status`]="{ item }">
      {{ capitalize(item.status!) }}
    </template>
    <template #[`item.actions`]="{ item }">
      <v-btn
        icon
        @click.stop="deleteReport(item.id)"
      >
        <v-icon>{{ $globals.icons.delete }}</v-icon>
      </v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import type { ReportSummary } from "~/lib/api/types/reports";

export default defineNuxtComponent({
  props: {
    items: {
      required: true,
      type: Array as () => Array<ReportSummary>,
    },
  },
  emits: ["delete"],

  setup(_, context) {
    const i18n = useI18n();
    const router = useRouter();

    const headers = [
      { title: i18n.t("category.category"), value: "category", key: "category" },
      { title: i18n.t("general.name"), value: "name", key: "name" },
      { title: i18n.t("general.timestamp"), value: "timestamp", key: "timestamp" },
      { title: i18n.t("general.status"), value: "status", key: "status" },
      { title: i18n.t("general.delete"), value: "actions", key: "actions" },
    ];

    function handleRowClick(item: ReportSummary) {
      if (item.status === "in-progress") {
        return;
      }

      router.push(`/group/reports/${item.id}`);
    }

    function capitalize(str: string) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }

    function deleteReport(id: string) {
      context.emit("delete", id);
    }

    return {
      headers,
      handleRowClick,
      capitalize,
      deleteReport,
    };
  },
});
</script>

<style lang="scss" scoped></style>
