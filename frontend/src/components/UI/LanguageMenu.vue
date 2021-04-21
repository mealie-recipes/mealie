<template>
  <div class="text-center">
    <v-menu
      transition="slide-x-transition"
      bottom
      right
      offset-y
      close-delay="200"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-btn v-bind="attrs" v-on="on" icon>
          <v-icon>mdi-translate</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item-group v-model="selectedItem" color="primary">
          <v-list-item
            v-for="(item, i) in allLanguages"
            :key="i"
            link
            @click="setLanguage(item.value)"
          >
            <v-list-item-content>
              <v-list-item-title>
                {{ item.name }}
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-menu>
  </div>
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
    let active = this.$store.getters.getActiveLang;
    this.allLanguages.forEach((element, index) => {
      if (element.value === active) {
        this.selectedItem = index;
        return;
      }
    });
  },
  computed: {
    allLanguages() {
      return this.$store.getters.getAllLangs;
    },
  },

  methods: {
    setLanguage(selectedLanguage) {
      if (this.siteSettings) {
        this.$emit(SELECT_EVENT, selectedLanguage);
      } else {
        this.$store.commit("setLang", selectedLanguage);
      }
    },
  },
};
</script>
<style>
.menu-text {
  text-align: left !important;
}
</style>