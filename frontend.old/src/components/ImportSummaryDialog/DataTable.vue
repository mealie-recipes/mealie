<template>
  <div>
    <v-data-table
      dense
      :headers="dataHeaders"
      :items="dataSet"
      item-key="name"
      class="elevation-1 mt-2"
      show-expand
      :expanded.sync="expanded"
      :footer-props="{
        'items-per-page-options': [100, 200, 300, 400, -1],
      }"
      :items-per-page="100"
    >
      <template v-slot:item.status="{ item }">
        <div :class="item.status ? 'success--text' : 'error--text'">
          {{ item.status ? "Imported" : "Failed" }}
        </div>
      </template>

      <template v-slot:expanded-item="{ headers, item }">
        <td :colspan="headers.length">
          <div class="ma-2">
            {{ item.exception }}
          </div>
        </td>
      </template>
    </v-data-table>
  </div>
</template>

<script>
export default {
  props: {
    dataSet: Array,
    dataHeaders: Array,
  },
  data: () => ({
    singleExpand: false,
    expanded: [],
  }),
};
</script>

<style></style>
