<template>
  <v-btn-toggle
    dense
    v-model="selected"
    tile
    color="primary accent-3"
    @change="emitChange"
    group
  >
    <v-btn value="include">
      Include
    </v-btn>

    <v-btn value="exclude">
      Exclude
    </v-btn>

    <v-btn value="any">
      Any
    </v-btn>
  </v-btn-toggle>
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
      selected: "include",
    };
  },
  methods: {
    emitChange() {
      this.$emit("input", this.selected);
    },
  },
};
</script>

<style lang="scss" scoped>
</style>