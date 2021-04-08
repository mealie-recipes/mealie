<template>
  <v-autocomplete
    :items="activeItems"
    v-model="selected"
    :value="value"
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
        :key="data.index"
      >
        {{ data.item.name || data.item }}
      </v-chip>
    </template>
    <template v-slot:append-outer="">
      <NewCategoryTagDialog
        v-if="showAdd"
        :tag-dialog="tagSelector"
        @created-item="pushToItem"
      />
    </template>
  </v-autocomplete>
</template>

<script>
import NewCategoryTagDialog from "@/components/UI/Dialogs/NewCategoryTagDialog";
const MOUNTED_EVENT = "mounted";
export default {
  components: {
    NewCategoryTagDialog,
  },
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
    showAdd: {
      default: false,
    },
    showLabel: {
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
    this.setInit(this.value);
  },

  watch: {
    value(val) {
      this.selected = val;
    },
  },

  computed: {
    inputLabel() {
      if (!this.showLabel) return null;
      return this.tagSelector ? "Tags" : "Categories";
    },
    activeItems() {
      let ItemObjects = [];
      if (this.tagSelector) ItemObjects = this.$store.getters.getAllTags;
      else {
        ItemObjects = this.$store.getters.getAllCategories;
      }
      if (this.returnObject) return ItemObjects;
      else {
        return ItemObjects.map(x => x.name);
      }
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
    pushToItem(createdItem) {
      createdItem = this.returnObject ? createdItem : createdItem.name;
      this.selected.push(createdItem);
    },
  },
};
</script>

<style lang="scss" scoped>
</style>