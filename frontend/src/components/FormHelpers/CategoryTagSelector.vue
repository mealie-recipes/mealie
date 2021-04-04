<template>
  <v-select
    :items="activeItems"
    v-model="selected"
    :label="inputLabel"
    chips
    deletable-chips
    :dense="dense"
    item-text="name"
    persistent-hint
    multiple
    :hint="hint"
    :solo="solo"
    :return-object="returnObject"
    :flat="flat"
    @input="emitChange"
  >
    <template v-slot:selection="data">
      <v-chip
        class="ma-1"
        :input-value="data.selected"
        close
        @click:close="removeByIndex(data.index)"
        label
        color="accent"
        dark
      >
        {{ data.item.name }}
      </v-chip>
    </template></v-select
  >
</template>

<script>
const MOUNTED_EVENT = "mounted";
export default {
  props: {
    value: Array,
    solo: {
      default: false,
    },
    dense: {
      default: true,
    },
    returnObject: {
      default: true,
    },
    tagSelector: {
      default: false,
    },
    hint: {
      default: null,
    },
  },
  data() {
    return {
      selected: [],
    };
  },
  mounted() {
    this.$emit(MOUNTED_EVENT);
  },

  watch: {
    value(val) {
      this.selected = val;
    },
  },

  computed: {
    inputLabel() {
      return this.tagSelector ? "Tags" : "Categories";
    },
    activeItems() {
      return this.tagSelector ? this.allTags : this.allCategories;
    },
    allCategories() {
      return this.$store.getters.getAllCategories;
    },
    allTags() {
      return this.$store.getters.getAllTags;
    },
    flat() {
      return this.selected.length > 0 && this.solo;
    },
  },
  methods: {
    emitChange() {
      this.$emit("input", this.selected);
    },
    setInit(val) {
      this.selected = val;
    },
    removeByIndex(index) {
      this.selected.splice(index, 1);
    },
  },
};
</script>

<style lang="scss" scoped>
</style>