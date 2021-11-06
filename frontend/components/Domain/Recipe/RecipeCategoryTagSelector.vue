//TODO: Prevent fetching Categories/Tags multiple time when selector is on page multiple times

<template>
  <v-autocomplete
    v-model="selected"
    :items="activeItems"
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
    :prepend-inner-icon="$globals.icons.tags"
    :flat="flat"
    v-bind="$attrs"
    @input="emitChange"
  >
    <template #selection="data">
      <v-chip
        v-if="showSelected"
        :key="data.index"
        :small="dense"
        class="ma-1"
        :input-value="data.selected"
        close
        label
        color="accent"
        dark
        @click:close="removeByIndex(data.index)"
      >
        {{ data.item.name || data.item }}
      </v-chip>
    </template>
    <template #append-outer="">
      <RecipeCategoryTagDialog v-if="showAdd" :tag-dialog="tagSelector" @created-item="pushToItem" />
    </template>
  </v-autocomplete>
</template>

<script>
import RecipeCategoryTagDialog from "./RecipeCategoryTagDialog";
import { useUserApi } from "~/composables/api";
import { useTags, useCategories } from "~/composables/use-tags-categories";
const MOUNTED_EVENT = "mounted";
export default {
  components: {
    RecipeCategoryTagDialog,
  },
  props: {
    value: {
      type: Array,
      required: true,
    },
    solo: {
      type: Boolean,
      default: false,
    },
    dense: {
      type: Boolean,
      default: true,
    },
    returnObject: {
      type: Boolean,
      default: true,
    },
    tagSelector: {
      type: Boolean,
      default: false,
    },
    hint: {
      type: String,
      default: null,
    },
    showAdd: {
      type: Boolean,
      default: false,
    },
    showLabel: {
      type: Boolean,
      default: true,
    },
    showSelected: {
      type: Boolean,
      default: true,
    },
  },

  setup() {
    const api = useUserApi();

    const { allTags, useAsyncGetAll: getAllTags } = useTags();
    const { allCategories, useAsyncGetAll: getAllCategories } = useCategories();
    getAllCategories();
    getAllTags();

    return { api, allTags, allCategories, getAllCategories, getAllTags };
  },

  data() {
    return {
      selected: [],
    };
  },

  computed: {
    inputLabel() {
      if (!this.showLabel) return null;
      return this.tagSelector ? this.$t("tag.tags") : this.$t("recipe.categories");
    },
    activeItems() {
      let ItemObjects = [];
      if (this.tagSelector) ItemObjects = this.allTags;
      else {
        ItemObjects = this.allCategories;
      }
      if (this.returnObject) return ItemObjects;
      else {
        return ItemObjects.map((x) => x.name);
      }
    },
    flat() {
      if (this.selected) {
        return this.selected.length > 0 && this.solo;
      }
      return false;
    },
  },

  watch: {
    value(val) {
      this.selected = val;
    },
  },
  mounted() {
    this.$emit(MOUNTED_EVENT);
    this.setInit(this.value);
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
      // TODO: Remove excessive get calls
      this.getAllCategories();
      this.getAllTags();
      this.selected.push(createdItem);
    },
  },
};
</script>

