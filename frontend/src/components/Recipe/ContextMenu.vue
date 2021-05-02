<template>
  <div class="text-center" v-if="loggedIn">
    <v-menu offset-y top left>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          :loading="loading"
          color="primary"
          icon
          dark
          v-bind="attrs"
          v-on="on"
          @click.prevent
        >
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>
      </template>
      <v-list dense>
        <v-list-item
          v-for="(item, index) in items"
          :key="index"
          @click="menuAction(item.action)"
        >
          <v-list-item-icon>
            <v-icon v-text="item.icon" :color="item.color"></v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script>
import { api } from "@/api";
export default {
  props: {
    slug: {
      type: String,
    },
  },
  computed: {
    loggedIn() {
      return this.$store.getters.getIsLoggedIn;
    },
    baseURL() {
      return window.location.origin;
    },
    recipeURL() {
      return `${this.baseURL}/recipe/${this.slug}`;
    },
  },
  data() {
    return {
      items: [
        {
          title: "Delete",
          icon: "mdi-delete",
          color: "error",
          action: "delete",
        },
        {
          title: "Edit",
          icon: "mdi-square-edit-outline",
          color: "accent",
          action: "edit",
        },
        {
          title: "Download",
          icon: "mdi-download",
          color: "accent",
          action: "download",
        },
        {
          title: "Link",
          icon: "mdi-content-copy",
          color: "accent",
          action: "share",
        },
      ],
      loading: false,
    };
  },
  methods: {
    async menuAction(action) {
      this.loading = true;

      switch (action) {
        case "delete":
          await api.recipes.delete(this.slug);
          break;
        case "share":
          this.updateClipboard();
          break;
        case "edit":
          this.$router.push(`/recipe/${this.slug}` + "?edit=true");
          break;
        case "download":
          console.log("Download");
          break;
        default:
          break;
      }

      this.loading = false;
    },
    updateClipboard() {
      const copyText = this.recipeURL;
      navigator.clipboard.writeText(copyText).then(
        function() {
          console.log("Copied", copyText);
        },
        function() {
          console.log("Copy Failed", copyText);
        }
      );
    },
  },
};
</script>