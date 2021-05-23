<template>
  <div class="d-print-none no-print">
    <v-navigation-drawer v-model="showSidebar" width="180px" clipped app>
      <template v-slot:prepend>
        <v-list-item two-line v-if="isLoggedIn" to="/admin/profile">
          <v-list-item-avatar color="accent" class="white--text">
            <img :src="userProfileImage" v-if="!hideImage" @error="hideImage = true" />
            <div v-else>
              {{ initials }}
            </div>
          </v-list-item-avatar>

          <v-list-item-content>
            <v-list-item-title> {{ user.fullName }}</v-list-item-title>
            <v-list-item-subtitle> {{ user.admin ? $t("user.admin") : $t("user.user") }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </template>
      <v-divider></v-divider>

      <v-list nav dense>
        <v-list-item v-for="nav in effectiveMenu" :key="nav.title" link :to="nav.to">
          <v-list-item-icon>
            <v-icon>{{ nav.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ nav.title }}</v-list-item-title>
        </v-list-item>
      </v-list>

      <!-- Version List Item -->
      <v-list nav dense class="fixedBottom" v-if="!isMain">
        <v-list-item to="/admin/about">
          <v-list-item-icon class="mr-3 pt-1">
            <v-icon :color="newVersionAvailable ? 'red--text' : ''">
              mdi-information
            </v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>
              {{ $t("settings.current") }}
              {{ appVersion }}
            </v-list-item-title>
            <v-list-item-subtitle>
              <a
                @click.prevent
                href="https://github.com/hay-kot/mealie/releases/latest"
                target="_blank"
                :class="newVersionAvailable ? 'red--text' : 'green--text'"
              >
                {{ $t("settings.latest") }}
                {{ latestVersion }}
              </a>
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<script>
import { initials } from "@/mixins/initials";
import { user } from "@/mixins/user";
import axios from "axios";
export default {
  mixins: [initials, user],
  data() {
    return {
      showSidebar: false,
      links: [],

      latestVersion: null,
      hideImage: false,
    };
  },
  mounted() {
    this.getVersion();
    this.resetView();
  },
  watch: {
    user() {
      this.hideImage = false;
    },
  },

  computed: {
    isMain() {
      const testVal = this.$route.path.split("/");
      if (testVal[1] === "recipe") this.closeSidebar();
      else this.resetView();

      return !(testVal[1] === "admin");
    },
    baseMainLinks() {
      return [
        {
          icon: "mdi-home",
          to: "/",
          title: this.$t("page.home-page"),
        },
        {
          icon: "mdi-magnify",
          to: "/search",
          title: this.$t("search.search"),
        },
        {
          icon: "mdi-view-module",
          to: "/recipes/all",
          title: this.$t("page.all-recipes"),
        },
        {
          icon: this.$globals.icons.tags,
          to: "/recipes/category",
          title: this.$t("recipe.categories"),
        },
        {
          icon: this.$globals.icons.tags,
          to: "/recipes/tag",
          title: this.$t("tag.tags"),
        },
      ];
    },
    customPages() {
      const pages = this.$store.getters.getCustomPages;
      if (pages.length > 0) {
        pages.sort((a, b) => a.position - b.position);
        return pages.map(x => ({
          title: x.name,
          to: `/pages/${x.slug}`,
          icon: this.$globals.icons.tags,
        }));
      }
      return [];
    },
    mainMenu() {
      return [...this.baseMainLinks, ...this.customPages];
    },
    settingsLinks() {
      return [
        {
          icon: this.$globals.icons.user,
          to: "/admin/profile",
          title: this.$t("settings.profile"),
        },
      ];
    },
    adminLinks() {
      return [
        {
          icon: "mdi-view-dashboard",
          to: "/admin/dashboard",
          title: this.$t("general.dashboard"),
        },
        {
          icon: "mdi-cog",
          to: "/admin/settings",
          title: this.$t("settings.site-settings"),
        },
        {
          icon: "mdi-tools",
          to: "/admin/toolbox",
          title: this.$t("settings.toolbox.toolbox"),
        },
        {
          icon: this.$globals.icons.group,
          to: "/admin/manage-users",
          title: this.$t("user.manage-users"),
        },
        {
          icon: "mdi-database-import",
          to: "/admin/migrations",
          title: this.$t("settings.migrations"),
        },
      ];
    },
    adminMenu() {
      if (this.user.admin) {
        return [...this.settingsLinks, ...this.adminLinks];
      } else {
        return this.settingsLinks;
      }
    },
    effectiveMenu() {
      return this.isMain ? this.mainMenu : this.adminMenu;
    },
    userProfileImage() {
      this.resetImage();
      return `api/users/${this.user.id}/image`;
    },
    newVersionAvailable() {
      return this.latestVersion == this.appVersion ? false : true;
    },
    appVersion() {
      const appInfo = this.$store.getters.getAppInfo;
      return appInfo.version;
    },
    isLoggedIn() {
      return this.$store.getters.getIsLoggedIn;
    },
    isMobile() {
      return this.$vuetify.breakpoint.name === "xs";
    },
  },

  methods: {
    resetImage() {
      this.hideImage == false;
    },
    resetView() {
      this.showSidebar = !this.isMobile;
    },
    toggleSidebar() {
      this.showSidebar = !this.showSidebar;
    },
    closeSidebar() {
      this.showSidebar = false;
    },
    async getVersion() {
      let response = await axios.get("https://api.github.com/repos/hay-kot/mealie/releases/latest", {
        headers: {
          "content-type": "application/json",
          Authorization: null,
        },
      });

      this.latestVersion = response.data.tag_name;
    },
  },
};
</script>

<style>
.fixedBottom {
  position: fixed !important;
  bottom: 0 !important;
  width: 100%;
}

@media print {
  .no-print {
    display: none;
  }
}
</style>
