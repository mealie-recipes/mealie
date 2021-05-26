<template>
  <SearchDialog ref="searchDialog">
    <template v-slot="{ open }">
      <v-text-field
        readonly
        @click="open"
        ref="searchInput"
        class="my-auto mt-5 pt-1"
        dense
        light
        dark
        flat
        :placeholder="$t('search.search-mealie')"
        background-color="primary lighten-1"
        color="white"
        solo=""
        :style="`max-width: 450;`"
      >
        <template #prepend-inner>
          <v-icon color="grey lighten-3" size="29">
            mdi-magnify
          </v-icon>
        </template>
      </v-text-field>
    </template>
  </SearchDialog>
</template>

<script>
import SearchDialog from "@/components/UI/Dialogs/SearchDialog";

export default {
  components: {
    SearchDialog,
  },

  mounted() {
    document.addEventListener("keydown", this.onDocumentKeydown);
  },
  beforeDestroy() {
    document.removeEventListener("keydown", this.onDocumentKeydown);
  },

  methods: {
    highlight(string) {
      if (!this.search) {
        return string;
      }
      return string.replace(new RegExp(this.search, "gi"), match => `<mark>${match}</mark>`);
    },

    onDocumentKeydown(e) {
      if (
        e.key === "/" &&
        e.target !== this.$refs.searchInput.$refs.input &&
        !document.activeElement.id.startsWith("input")
      ) {
        e.preventDefault();
        this.$refs.searchDialog.open();
      }
    },
  },
};
</script>

