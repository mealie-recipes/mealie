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
import api from "@/api";
export default {
  props: {
    value: Array,
  },
  data() {
    return {
      selected: [],
      allCategories: [],
    };
  },
  watch: {
    value() {
      this.selected = this.value;
    },
  },
  async created() {
    this.allCategories = await api.categories.get_all();
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