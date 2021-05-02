<template>
  <v-select
    dense
    :items="allLanguages"
    item-text="name"
    :label="$t('settings.language')"
    prepend-icon="mdi-translate"
    :value="selectedItem"
    @input="setLanguage"
  >
  </v-select>
</template>

<script>
const SELECT_EVENT = "select-lang";
export default {
  props: {
    siteSettings: {
      default: false,
    },
  },
  data: function() {
    return {
      selectedItem: 0,
      items: [
        {
          name: "English",
          value: "en-US",
        },
      ],
    };
  },
  mounted() {
    this.selectedItem = this.$store.getters.getActiveLang;
  },
  computed: {
    allLanguages() {
      return this.$store.getters.getAllLangs;
    },
  },

  methods: {
    setLanguage(selectedLanguage) {
      this.$emit(SELECT_EVENT, selectedLanguage);
    },
  },
};
</script>
