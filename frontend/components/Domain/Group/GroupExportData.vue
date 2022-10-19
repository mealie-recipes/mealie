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
import { defineComponent, useContext } from "@nuxtjs/composition-api";
import { parseISO, formatDistanceToNow } from "date-fns";
import { GroupDataExport } from "~/lib/api/types/group";
export default defineComponent({
  props: {
    exports: {
      type: Array as () => GroupDataExport[],
      required: true,
    },
  },
  setup() {
    const { i18n } = useContext();

    const headers = [
      { text: i18n.t("export.export"), value: "name" },
      { text: i18n.t("export.file-name"), value: "filename" },
      { text: i18n.t("export.size"), value: "size" },
      { text: i18n.t("export.link-expires"), value: "expires" },
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
