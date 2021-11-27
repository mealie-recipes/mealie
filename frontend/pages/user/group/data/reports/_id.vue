<template>
  <v-container>
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="200" max-width="200" class="mb-2" :src="require('~/static/svgs/data-reports.svg')"></v-img>
      </template>
      <template #title> Recipe Data Migrations</template>
      Recipes can be migrated from another supported application to Mealie. This is a great way to get started with
      Mealie.
    </BasePageTitle>
    <v-container v-if="report">
      <BaseCardSectionTitle :title="report.name"> </BaseCardSectionTitle>

      <v-card-text> Report Id: {{ id }} </v-card-text>

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
          <td class="pa-6" :colspan="headers.length">{{ item.exception }}</td>
        </template>
      </v-data-table>
    </v-container>
  </v-container>
</template>

<script>
import { defineComponent, useRoute, reactive, toRefs, onMounted } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";

export default defineComponent({
  setup() {
    const route = useRoute();
    const id = route.value.params.id;

    const api = useUserApi();

    const state = reactive({
      report: {},
    });

    async function getReport() {
      const { data } = await api.groupReports.getOne(id);

      if (data) {
        state.report = data;
      }
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
      ...toRefs(state),
      id,
      itemHeaders,
    };
  },
});
</script>

<style lang="scss" scoped>
</style>