<template>
  <div>
    <base-dialog
      ref="assignDialog"
      title-icon="mdi-tag"
      color="primary"
      title="Bulk Assign"
      :loading="loading"
      modal-width="700"
      :top="true"
    >
      <v-card-text>
        <v-text-field
          v-model="search"
          autocomplete="off"
          label="Keyword"
        ></v-text-field>
        <CategoryTagSelector
          :tag-selector="false"
          v-model="catsToAssign"
          :return-object="false"
        />
        <CategoryTagSelector
          :tag-selector="true"
          v-model="tagsToAssign"
          :return-object="false"
        />
      </v-card-text>
      <template slot="card-actions">
        <v-btn text color="grey" @click="closeDialog">
          Cancel
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          color="success"
          @click="assignAll"
          :loading="loading"
          :disabled="results.length < 1"
        >
          Assign All
        </v-btn>
      </template>
      <template slot="below-actions">
        <v-card-title class="headline"> </v-card-title>
        <CardSection
          class="px-2 pb-2"
          :title="`${results.length || 0} Recipes Effected`"
          :mobile-cards="true"
          :recipes="results"
          :single-column="true"
        />
      </template>
    </base-dialog>

    <v-btn @click="openDialog" small color="success" class="mr-1">
      Bulk Assign
    </v-btn>
  </div>
</template>

<script>
import CardSection from "@/components/UI/CardSection";
import CategoryTagSelector from "@/components/FormHelpers/CategoryTagSelector";
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
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
  computed: {
    allRecipes() {
      return this.$store.getters.getRecentRecipes;
    },
    results() {
      if (this.search === null || this.search === "") {
        return [];
      }
      return this.allRecipes.filter(x => {
        return (
          this.checkForKeywords(x.name) || this.checkForKeywords(x.description)
        );
      });
    },
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
      console.log("Categories", this.catsToAssign);
      console.log("Tags", this.tagsToAssign);
      console.log("results", this.results);
    },
    closeDialog() {
      this.$refs.assignDialog.close();
    },
    async openDialog() {
      this.$refs.assignDialog.open();
      this.reset();
    },
    checkForKeywords(str) {
      const searchStr = str.toLowerCase();
      return this.keywords.some(x => searchStr.includes(x));
    },
  },
};
</script>

<style lang="scss" scoped>
</style>