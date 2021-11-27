<template>
  <v-data-table
    :headers="headers"
    :items="items"
    item-key="id"
    class="elevation-0"
    :items-per-page="50"
    @click:row="handleRowClick"
  >
    <template #item.category="{ item }">
      {{ capitalize(item.category) }}
    </template>
    <template #item.timestamp="{ item }">
      {{ $d(Date.parse(item.timestamp), "long") }}
    </template>
    <template #item.status="{ item }">
      {{ capitalize(item.status) }}
    </template>
    <template #item.actions="{ item }">
      <v-btn icon @click.stop="deleteReport(item.id)">
        <v-icon>{{ $globals.icons.delete }}</v-icon>
      </v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { defineComponent, useRouter } from "@nuxtjs/composition-api";
import { ReportSummary } from "~/api/class-interfaces/group-reports";

export default defineComponent({
  props: {
    items: {
      required: true,
      type: Array as () => Array<ReportSummary>,
    },
  },

  setup(_, context) {
    const router = useRouter();

    const headers = [
      { text: "Category", value: "category" },
      { text: "Name", value: "name" },
      { text: "Timestamp", value: "timestamp" },
      { text: "Status", value: "status" },
      { text: "Delete", value: "actions" },
    ];

    function handleRowClick(item: any) {
      router.push("/user/group/data/reports/" + item.id);
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

<style lang="scss" scoped>
</style>