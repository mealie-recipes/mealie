<template>
  <v-select
    :items="allTags"
    v-model="selected"
    label="Tags"
    chips
    deletable-chips
    :dense="dense"
    :solo="solo"
    :flat="flat"
    item-text="name"
    multiple
    :return-object="returnObject"
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
    </template>
  </v-select>
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