<template>
  <v-data-table
    item-key="id"
    :headers="headers"
    :items="exports"
    :items-per-page="15"
    class="elevation-0"
    @click:row="downloadData"
  >
    <template #item.expires="{ item }">
      {{ getTimeToExpire(item.expires) }}
    </template>
    <template #item.actions="{ item }">
      <BaseButton download small :download-url="`/api/recipes/bulk-actions/export/download?path=${item.path}`">
      </BaseButton>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { parseISO, formatDistanceToNow } from "date-fns";
import { GroupDataExport } from "~/api/class-interfaces/recipe-bulk-actions";
export default defineComponent({
  props: {
    exports: {
      type: Array as () => GroupDataExport[],
      required: true,
    },
  },
  setup() {
    const headers = [
      { text: "Export", value: "name" },
      { text: "File Name", value: "filename" },
      { text: "Size", value: "size" },
      { text: "Link Expires", value: "expires" },
      { text: "", value: "actions" },
    ];

    function getTimeToExpire(timeString: string) {
      const expiresAt = parseISO(timeString);

      return formatDistanceToNow(expiresAt, {
        addSuffix: false,
      });
    }

    function downloadData(_: any) {
      console.log("Downloading data...");
    }

    return {
      downloadData,
      headers,
      getTimeToExpire,
    };
  },
});
</script>

