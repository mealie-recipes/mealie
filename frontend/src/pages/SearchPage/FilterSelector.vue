<template>
  <v-toolbar dense flat>
    <v-btn-toggle
      dense
      v-model="selected"
      tile
      color="primary accent-3"
      @change="emitMulti"
      group
      mandatory
    >
      <v-btn :value="false">
        Include
      </v-btn>

      <v-btn :value="true">
        Exclude
      </v-btn>
    </v-btn-toggle>
    <v-spacer></v-spacer>
    <v-btn-toggle
      dense
      v-model="match"
      tile
      color="primary accent-3"
      @change="emitMulti"
      group
      mandatory
    >
      <v-btn :value="false">
        And
      </v-btn>
      <v-btn :value="true">
        Or
      </v-btn>
    </v-btn-toggle>
  </v-toolbar>
</template>

<script>
export default {
  props: {
    value: {
      default: "include", // Optionas: "include", "exclude", "any"
    },
  },
  data() {
    return {
      selected: false,
      match: false,
    };
  },
  methods: {
    emitChange() {
      this.$emit("input", this.selected);
    },
    emitMulti() {
      const updateData = {
        exclude: this.selected,
        matchAny: this.match,
      };
      this.$emit("update", updateData);
    },
  },
};
</script>

<style lang="scss" scoped>
</style>