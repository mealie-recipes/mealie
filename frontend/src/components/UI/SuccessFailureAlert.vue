<template>
  <v-dialog v-model="dialog" max-width="900px">
    <v-card>
      <v-card-title> {{ title }} </v-card-title>
      <v-card-text class="mt-3">
        <v-row>
          <v-col>
            <v-alert outlined dense type="success">
              <h4>{{ successHeader }}</h4>
              <p v-for="success in this.success" :key="success" class="my-1">
                - {{ success }}
              </p>
            </v-alert>
          </v-col>
          <v-col>
            <v-alert v-if="failed[0]" outlined dense type="error">
              <h4>{{ failedHeader }}</h4>
              <p v-for="fail in this.failed" :key="fail" class="my-1">
                - {{ fail }}
              </p>
            </v-alert>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    title: String,
    successHeader: String,
    success: Array,
    failedHeader: String,
    failed: Array,
  },
  data() {
    return {
      dialog: false,
    };
  },
  methods: {
    open() {
      this.dialog = true;
    },
  },
};
</script>

<style>
</style>