<template>
  <v-data-table
    item-key="id"
    :headers="headers"
    :items="exports"
    :items-per-page="15"
    class="elevation-0"
    @click:row="downloadData"
  >
    <template #[`item.expires`]="{ item }">
      {{ getTimeToExpire(item.expires) }}
    </template>
    <template #[`item.actions`]="{ item }">
      <BaseButton
        download
        size="small"
        :download-url="`/api/recipes/bulk-actions/export/download?path=${item.path}`"
      />
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { parseISO, formatDistanceToNow } from "date-fns";
import type { GroupDataExport } from "~/lib/api/types/group";

export default defineNuxtComponent({
  props: {
    exports: {
      type: Array as () => GroupDataExport[],
      required: true,
    },
  },
  setup() {
    const i18n = useI18n();

    const headers = [
      { title: i18n.t("export.export"), value: "name" },
      { title: i18n.t("export.file-name"), value: "filename" },
      { title: i18n.t("export.size"), value: "size" },
      { title: i18n.t("export.link-expires"), value: "expires" },
      { title: "", value: "actions" },
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
