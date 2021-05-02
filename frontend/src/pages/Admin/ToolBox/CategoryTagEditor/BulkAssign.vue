<template>
  <div>
    <base-dialog
      ref="assignDialog"
      title-icon="mdi-tag"
      color="primary"
      :title="$t('settings.toolbox.bulk-assign')"
      :loading="loading"
      modal-width="700"
      :top="true"
    >
      <v-card-text>
        <v-text-field v-model="search" autocomplete="off" :label="$t('general.keyword')"></v-text-field>
        <CategoryTagSelector :tag-selector="false" v-model="catsToAssign" :return-object="false" />
        <CategoryTagSelector :tag-selector="true" v-model="tagsToAssign" :return-object="false" />
      </v-card-text>
      <template slot="card-actions">
        <v-btn text color="grey" @click="closeDialog">
          {{ $t("general.cancel") }}
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn color="success" @click="assignAll" :loading="loading" :disabled="results.length < 1">
          {{ $t("settings.toolbox.assign-all") }}
        </v-btn>
      </template>
      <template slot="below-actions">
        <v-card-title class="headline"> </v-card-title>
        <CardSection
          class="px-2 pb-2"
          :title="$tc('settings.toolbox.recipes-affected', results.length || 0)"
          :mobile-cards="true"
          :recipes="results"
          :single-column="true"
        />
      </template>
    </base-dialog>

    <v-btn @click="openDialog" small color="success">
      {{ $t("settings.toolbox.bulk-assign") }}
    </v-btn>
  </div>
</template>

<script>
import CardSection from "@/components/UI/CardSection";
import CategoryTagSelector from "@/components/FormHelpers/CategoryTagSelector";
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import { api } from "@/api";
export default {
  props: {
    isTags: {
      default: true,
    },
  },
  components: {
    CardSection,
    BaseDialog,
    CategoryTagSelector,
  },
  data() {
    return {
      results: [],
      search: "",
      loading: false,
      assignTargetRecipes: [],
      catsToAssign: [],
      tagsToAssign: [],
    };
  },
  mounted() {
    this.$store.dispatch("requestAllRecipes");
  },
  watch: {
    search() {
      this.getResults();
    },
  },
  computed: {
    allRecipes() {
      return this.$store.getters.getAllRecipes;
    },
    // results() {
    //   if (this.search === null || this.search === "") {
    //     return [];
    //   }
    //   return this.allRecipes.filter(x => {
    //     return (
    //       this.checkForKeywords(x.name) || this.checkForKeywords(x.description)
    //     );
    //   });
    // },
    keywords() {
      const lowered = this.search.toLowerCase();
      return lowered.split(" ");
    },
  },
  methods: {
    reset() {
      this.search = "";
      this.loading = false;
      this.assignTargetRecipes = [];
      this.catsToAssign = [];
      this.tagsToAssign = [];
    },
    assignAll() {
      this.loading = true;
      this.results.forEach(async element => {
        element.recipeCategory = element.recipeCategory.concat(this.catsToAssign);
        element.tags = element.tags.concat(this.tagsToAssign);
        await api.recipes.patch(element);
      });
      this.loading = false;
      this.closeDialog();
    },
    closeDialog() {
      this.$refs.assignDialog.close();
    },
    async openDialog() {
      this.$refs.assignDialog.open();
      this.reset();
    },
    getResults() {
      this.loading = true;

      // cancel pending call
      clearTimeout(this._timerId);
      this._timerId = setTimeout(() => {
        this.results = this.filterResults();
      }, 300);
      this.loading = false;
      // delay new call 500ms
    },
    filterResults() {
      if (this.search === null || this.search === "") {
        return [];
      }
      return this.allRecipes.filter(x => {
        return this.checkForKeywords(x.name) || this.checkForKeywords(x.description);
      });
    },
    checkForKeywords(str) {
      const searchStr = str.toLowerCase();
      return this.keywords.some(x => searchStr.includes(x));
    },
  },
};
</script>

<style lang="scss" scoped></style>
