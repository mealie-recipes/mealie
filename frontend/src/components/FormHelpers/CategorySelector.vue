<template>
  <div>
    <v-select
      :items="allCategories"
      v-model="selected"
      label="Categories"
      chips
      deletable-chips
      dense
      item-text="name"
      multiple
      return-object
      @input="emitChange"
    ></v-select>
  </div>
</template>

<script>
const MOUNTED_EVENT = "mounted";
export default {
  props: {
    value: Array,
  },
  data() {
    return {
      selected: [],
    };
  },
  mounted() {
    this.$emit(MOUNTED_EVENT);
  },

  computed: {
    allCategories() {
      return this.$store.getters.getAllCategories;
    },
  },
  methods: {
    emitChange() {
      this.$emit("input", this.selected);
    },
    setInit(val) {
      this.selected = val;
    },
  },
};
</script>

<style lang="scss" scoped>
</style>