<template>
  <v-dialog v-model="pageDialog" max-width="500">
    <v-card>
      <v-app-bar dark dense color="primary">
        <v-icon left>
          mdi-page-layout-body
        </v-icon>

        <v-toolbar-title class="headline">
          {{ title }}
        </v-toolbar-title>

        <v-spacer></v-spacer>
      </v-app-bar>
      <v-form ref="newGroup" @submit="submitForm">
        <v-card-text>
          <v-text-field
            autofocus
            v-model="page.name"
            label="Page Name"
          ></v-text-field>
          <CategorySelector v-model="page.categories" />
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" text @click="pageDialog = false">
            {{ $t("general.cancel") }}
          </v-btn>
          <v-btn color="primary" type="submit">
            {{ buttonText }}
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
const NEW_PAGE_EVENT = "refresh-page";
import api from "@/api";
import CategorySelector from "@/components/FormHelpers/CategorySelector";
export default {
  components: {
    CategorySelector,
  },
  data() {
    return {
      title: "",
      buttonText: "",
      create: false,
      pageDialog: false,
      page: {
        name: "",
        position: 0,
        categories: [],
      },
    };
  },
  mounted() {
    this.page = {
      name: "",
      position: 0,
      categories: [],
    };
  },
  watch: {
    page() {
      console.log(this.page);
    },
  },
  methods: {
    open(parameters) {
      this.page = parameters.data;
      this.create = parameters.create;
      this.buttonText = parameters.buttonText;
      this.title = parameters.title;
      this.pageDialog = true;
    },
    async submitForm() {
      if (this.create) {
        await api.siteSettings.createPage(this.page);
      } else {
        await api.siteSettings.updatePage(this.page);
      }
      this.pageDialog = false;
      this.page.categories = [];
      this.$emit(NEW_PAGE_EVENT);
    },
  },
};
</script>

<style lang="scss" scoped>
</style>