<template>
  <v-dialog
    ref="dialog"
    v-model="modal2"
    :return-value.sync="time"
    persistent
    width="290px"
  >
    <template v-slot:activator="{ on, attrs }">
      <v-text-field
        v-model="time"
        label="Set New Time"
        prepend-icon="mdi-clock-time-four-outline"
        readonly
        v-bind="attrs"
        v-on="on"
      ></v-text-field>
    </template>
    <v-time-picker v-if="modal2" v-model="time" full-width>
      <v-spacer></v-spacer>
      <v-btn text color="primary" @click="modal2 = false"> Cancel </v-btn>
      <v-btn text color="primary" @click="saveTime"> OK </v-btn>
    </v-time-picker>
  </v-dialog>
</template>

<script>
export default {
  data() {
    return {
      time: null,
      modal2: false,
    };
  },
  methods: {
    saveTime() {
      this.$refs.dialog.save(this.time);
      this.$emit("save-time", this.time);
    },
  },
};
</script>

<style scoped>
</style>