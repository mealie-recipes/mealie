<template>
  <div class="text-center">
    <ConfirmationDialog
      :title="$t('recipe.delete-recipe')"
      :message="$t('recipe.delete-confirmation')"
      color="error"
      icon="mdi-alert-circle"
      ref="deleteRecipieConfirm"
      v-on:confirm="deleteRecipe()"
    />
    <v-menu offset-y top left>
      <template v-slot:activator="{ on, attrs }">
        <v-btn color="primary" icon dark v-bind="attrs" v-on="on" @click.prevent>
          <v-icon>{{ menuIcon }}</v-icon>
        </v-btn>
      </template>
      <v-list dense>
        <v-list-item
          v-for="(item, index) in loggedIn ? userMenu : defaultMenu"
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
import ConfirmationDialog from "@/components/UI/Dialogs/ConfirmationDialog.vue";
import { api } from "@/api";
export default {
  components: {
    ConfirmationDialog,
  },
  props: {
    slug: {
      type: String,
    },
    menuIcon: {
      default: "mdi-dots-vertical",
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
    defaultMenu() {
      return [
        {
          title: this.$t("general.download"),
          icon: "mdi-download",
          color: "accent",
          action: "download",
        },
        {
          title: this.$t("general.link"),
          icon: "mdi-content-copy",
          color: "accent",
          action: "share",
        },
      ];
    },
    userMenu() {
      return [
        {
          title: this.$t("general.delete"),
          icon: "mdi-delete",
          color: "error",
          action: "delete",
        },
        {
          title: this.$t("general.edit"),
          icon: "mdi-square-edit-outline",
          color: "accent",
          action: "edit",
        },
        ...this.defaultMenu,
      ];
    },
  },
  data() {
    return {
      loading: true,
    };
  },
  methods: {
    async menuAction(action) {
      this.loading = true;

      switch (action) {
        case "delete":
          this.$refs.deleteRecipieConfirm.open();
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
    async deleteRecipe() {
      await api.recipes.delete(this.slug);
    },
    updateClipboard() {
      const copyText = this.recipeURL;
      navigator.clipboard.writeText(copyText).then(
        () => console.log("Copied", copyText),
        () => console.log("Copied Failed", copyText)
      );
    },
  },
};
</script>
