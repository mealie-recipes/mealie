<template>
  <div class="text-center">
    <BaseDialog
      ref="confirmDelete"
      :title="$t('recipe.delete-recipe')"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="deleteRecipe()"
    >
      <v-card-text>
        {{ $t("recipe.delete-confirmation") }}
      </v-card-text>
    </BaseDialog>
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
      content-class="d-print-none"
    >
      <template #activator="{ on, attrs }">
        <v-btn :fab="fab" :small="fab" :color="color" :icon="!fab" dark v-bind="attrs" v-on="on" @click.prevent>
          <v-icon>{{ effMenuIcon }}</v-icon>
        </v-btn>
      </template>
      <v-list dense>
        <v-list-item v-for="(item, index) in displayedMenu" :key="index" @click="menuAction(item.action)">
          <v-list-item-icon>
            <v-icon :color="item.color" v-text="item.icon"></v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script>
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
import { alert } from "~/composables/use-toast";
export default defineComponent({
  props: {
    menuTop: {
      type: Boolean,
      default: true,
    },
    showPrint: {
      type: Boolean,
      default: false,
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
      required: true,
    },
    menuIcon: {
      type: String,
      default: null,
    },
    name: {
      required: true,
      type: String,
    },
    cardMenu: {
      type: Boolean,
      default: true,
    },
  },
  setup() {
    const api = useApiSingleton();
    const confirmDelete = ref(null);
    return { api, confirmDelete };
  },
  data() {
    return {
      loading: true,
    };
  },
  computed: {
    effMenuIcon() {
      return this.menuIcon ? this.menuIcon : this.$globals.icons.dotsVertical;
    },
    loggedIn() {
      return this.$auth.loggedIn;
    },
    baseURL() {
      return window.location.origin;
    },
    recipeURL() {
      return `${this.baseURL}/recipe/${this.slug}`;
    },
    printerMenu() {
      return {
        title: this.$t("general.print"),
        icon: this.$globals.icons.printer,
        color: "accent",
        action: "print",
      };
    },
    defaultMenu() {
      return [
        {
          title: this.$t("general.share"),
          icon: this.$globals.icons.shareVariant,
          color: "accent",
          action: "share",
        },
        {
          title: this.$t("general.download"),
          icon: this.$globals.icons.download,
          color: "accent",
          action: "download",
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
      ];
    },
    displayedMenu() {
      let menu = this.defaultMenu;
      if (this.loggedIn && this.cardMenu) {
        menu = [...this.userMenu, ...menu];
      }
      if (this.showPrint) {
        menu = [this.printerMenu, ...menu];
      }
      return menu;
    },
    recipeText() {
      return this.$t("recipe.share-recipe-message", [this.name]);
    },
  },
  methods: {
    menuAction(action) {
      this.loading = true;

      switch (action) {
        case "delete":
          this.confirmDelete.open();
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
              .catch((error) => {
                console.log("WebShareAPI not supported", error);
                this.updateClipboard();
              });
          } else this.updateClipboard();
          break;
        case "edit":
          this.$router.push(`/recipe/${this.slug}` + "?edit=true");
          break;
        case "print":
          this.$emit("print");
          break;
        case "download":
          window.open(`/api/recipes/${this.slug}/zip`);
          break;
        default:
          break;
      }

      this.loading = false;
    },
    async deleteRecipe() {
      console.log("Delete Called");
      await this.api.recipes.deleteOne(this.slug);
    },
    updateClipboard() {
      const copyText = this.recipeURL;
      navigator.clipboard.writeText(copyText).then(
        () => {
          console.log("Copied to Clipboard", copyText);
          alert.success("Recipe link copied to clipboard");
        },
        () => {
          console.log("Copied Failed", copyText);
          alert.error("Copied Failed");
        }
      );
    },
  },
});
</script>
