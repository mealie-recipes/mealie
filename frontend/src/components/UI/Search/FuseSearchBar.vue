<template>
  <div>
    <slot> </slot>
  </div>
</template>

<script>
const RESULTS_EVENT = "results";
import Fuse from "fuse.js";

export default {
  props: {
    search: {
      default: "",
    },
    rawData: {
      default: true,
    },
    /** Defaults to Show All Results  */
    showAll: {
      default: true,
    },
    keys: {
      type: Array,
      default: () => ["name"],
    },
    defaultOptions: {
      default: () => ({
        shouldSort: true,
        threshold: 0.6,
        location: 0,
        distance: 100,
        findAllMatches: true,
        maxPatternLength: 32,
        minMatchCharLength: 2,
      }),
    },
  },
  data() {
    return {
      results: [],
      fuseResults: [],
    };
  },
  computed: {
    options() {
      return { ...this.defaultOptions, ...{ keys: this.keys } };
    },
    autoResults() {
      return this.fuseResults.length > 1 ? this.fuseResults : this.results;
    },
    fuse() {
      return new Fuse(this.rawData, this.options);
    },
    isSearching() {
      return this.search && this.search.length > 0;
    },
  },
  watch: {
    search() {
      try {
        this.results = this.fuse.search(this.search.trim());
      } catch {
        this.results = this.rawData.map(x => ({ item: x })).sort((a, b) => (a.name > b.name ? 1 : -1));
      }
      this.$emit(RESULTS_EVENT, this.results);

      if (this.showResults === true) {
        this.fuseResults = this.results;
      }
    },
  },
};
</script>

<style scoped></style>
