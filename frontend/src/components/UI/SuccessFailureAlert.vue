<template>
  <div>
    <v-alert v-if="success[0]" outlined dense type="success">
      <h4>{{ successHeader }}</h4>
      <v-list dense>
        <v-list-item v-for="success in this.success" :key="success">
          {{ success }}
        </v-list-item>
      </v-list>
    </v-alert>
    <v-alert v-if="failed[0]" outlined dense type="error">
      <h4>{{ failedHeader }}</h4>
      <v-list dense>
        <v-list-item v-for="fail in this.failed" :key="fail">
          {{ fail }}
        </v-list-item>
      </v-list>
    </v-alert>
  </div>
</template>

<script>
export default {
  props: {
    successHeader: String,
    success: Array,
    failedHeader: String,
    failed: Array,
  },
};
</script>

<style>
</style>