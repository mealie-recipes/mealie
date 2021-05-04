<template>
  <v-card outlined class="mt-n1">
    <div class="d-flex justify-center align-center pa-2 flex-wrap">
      <v-btn-toggle v-model="filter" mandatory color="primary">
        <v-btn small value="category">
          <v-icon>mdi-tag-multiple</v-icon>
          {{ $t("category.category") }}
        </v-btn>

        <v-btn small value="tag">
          <v-icon>mdi-tag-multiple</v-icon>
          {{ $t("tag.tags") }}
        </v-btn>
      </v-btn-toggle>
      <v-spacer v-if="!isMobile"> </v-spacer>

      <FuseSearchBar :raw-data="allItems" @results="filterItems" :search="searchString">
        <v-text-field
          v-model="searchString"
          clearable
          solo
          dense
          class="mx-2"
          hide-details
          single-line
          :placeholder="$t('search.search')"
          prepend-inner-icon="mdi-magnify"
        >
        </v-text-field>
      </FuseSearchBar>
    </div>
  </v-card>
</template>

<script>
import FuseSearchBar from "@/components/UI/Search/FuseSearchBar";
export default {
  components: { FuseSearchBar },
  data() {
    return {
      buttonToggle: 0,
      allItems: [],
      searchString: "",
      searchResults: [],
    };
  },
  computed: {
    isMobile() {
      return this.$vuetify.breakpoint.name === "xs";
    },
    isCategory() {
      return this.buttonToggle === 0;
    },
    filter: {
      set(filter) {
        this.$router.replace({ query: { ...this.$route.query, filter } });
      },
      get() {
        return this.$route.query.filter;
      },
    },
  },
  methods: {
    filterItems(val) {
      this.searchResults = val.map(x => x.item);
    },
  },
};
</script>

<style lang="scss" scoped>
</style>