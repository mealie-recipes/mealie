<template>
  <div class="text-center">
    <ConfirmationDialog
      :title="$t('recipe.delete-recipe')"
      :message="$t('recipe.delete-confirmation')"
      color="error"
      :icon="$globals.icons.alertCircle"
      ref="deleteRecipieConfirm"
      v-on:confirm="deleteRecipe()"
    />
    <v-menu
      offset-y
      left
      :bottom="!menuTop"
      :nudge-bottom="!menuTop ? '5' : '0'"
      :top="menuTop"
      :nudge-top="menuTop ? '5' : '0'"
      allow-overflow
      close-delay="125"
      open-on-hover
    >
      <template v-slot:activator="{ on, attrs }">
        <v-btn :fab="fab" :small="fab" :color="color" :icon="!fab" dark v-bind="attrs" v-on="on" @click.prevent>
          <v-icon>{{ effMenuIcon }}</v-icon>
        </v-btn>
      </template>
      <v-list dense>
        <v-list-item
          v-for="(item, index) in loggedIn && cardMenu ? userMenu : defaultMenu"
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
import { utils } from "@/utils";
export default {
  components: {
    ConfirmationDialog,
  },
  props: {
    menuTop: {
      type: Boolean,
      default: true,
    },
    fab: {
      type: Boolean,
      default: false,
    },
    color: {
      type: String,
      default: "primary",
    },
    slug: {
      type: String,
    },
    menuIcon: {
      default: null,
    },
    name: {
      type: String,
    },
    cardMenu: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    effMenuIcon() {
      return this.menuIcon ? this.menuIcon : this.$globals.icons.dotsVertical;
    },
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
          title: this.$t("general.print"),
          icon: this.$globals.icons.printer,
          color: "accent",
          action: "print",
        },
        {
          title: this.$t("general.share"),
          icon: this.$globals.icons.shareVariant,
          color: "accent",
          action: "share",
        },
      ];
    },
    userMenu() {
      return [
        {
          title: this.$t("general.delete"),
          icon: this.$globals.icons.delete,
          color: "error",
          action: "delete",
        },
        {
          title: this.$t("general.edit"),
          icon: this.$globals.icons.edit,
          color: "accent",
          action: "edit",
        },
        ...this.defaultMenu,
      ];
    },
    recipeText() {
      return this.$t("recipe.share-recipe-message", [this.name]);
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
          if (navigator.share) {
            navigator
              .share({
                title: this.name,
                text: this.recipeText,
                url: this.recipeURL,
              })
              .then(() => console.log("Successful share"))
              .catch(error => {
                console.log("WebShareAPI not supported", error);
                this.updateClipboard();
              });
          } else this.updateClipboard();
          break;
        case "edit":
          this.$router.push(`/recipe/${this.slug}` + "?edit=true");
          break;
        case "print":
          this.$router.push(`/recipe/${this.slug}` + "?print=true");
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
        () => {
          console.log("Copied to Clipboard", copyText);
          utils.notify.success("Copied to Clipboard");
        },
        () => console.log("Copied Failed", copyText)
      );
    },
  },
};
</script>
