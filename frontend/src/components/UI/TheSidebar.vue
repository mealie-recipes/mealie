<template>
  <div>
    <v-navigation-drawer
      :value="mobile ? showSidebar : true"
      v-model="showSidebar"
      width="180px"
      clipped
      app
    >
      <template v-slot:prepend>
        <v-list-item two-line v-if="isLoggedIn">
          <v-list-item-avatar color="accent" class="white--text">
            <img
              :src="userProfileImage"
              v-if="!hideImage"
              @error="hideImage = true"
            />
            <div v-else>
              {{ initials }}
            </div>
          </v-list-item-avatar>

          <v-list-item-content>
            <v-list-item-title> {{ user.fullName }}</v-list-item-title>
            <v-list-item-subtitle>
              {{ user.admin ? "Admin" : "User" }}</v-list-item-subtitle
            >
          </v-list-item-content>
        </v-list-item>
      </template>
      <v-divider></v-divider>

      <v-list nav dense>
        <v-list-item
          v-for="nav in effectiveMenu"
          :key="nav.title"
          link
          :to="nav.to"
        >
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
      mobile: false,
      links: [],
      baseMainLinks: [
        {
          icon: "mdi-home",
          to: "/",
          title: this.$t("page.home-page"),
        },
        {
          icon: "mdi-view-module",
          to: "/recipes/all",
          title: this.$t("page.all-recipes"),
        },
        {
          icon: "mdi-magnify",
          to: "/search",
          title: this.$t("search.search"),
        },
      ],
      latestVersion: null,
      hideImage: false,
      settingsLinks: [
        {
          icon: "mdi-account",
          to: "/admin/profile",
          title: this.$t("settings.profile"),
        },
        {
          icon: "mdi-format-color-fill",
          to: "/admin/themes",
          title: this.$t("general.themes"),
        },
        {
          icon: "mdi-food",
          to: "/admin/meal-planner",
          title: this.$t("meal-plan.meal-planner"),
        },
      ],
      adminLinks: [
        {
          icon: "mdi-cog",
          to: "/admin/settings",
          title: this.$t("settings.site-settings"),
        },
        {
          icon: "mdi-account-group",
          to: "/admin/manage-users",
          title: this.$t("settings.manage-users"),
        },
        {
          icon: "mdi-backup-restore",
          to: "/admin/backups",
          title: this.$t("settings.backup-and-exports"),
        },
        {
          icon: "mdi-database-import",
          to: "/admin/migrations",
          title: this.$t("settings.migrations"),
        },
      ],
    };
  },
  mounted() {
    this.getVersion();
    this.resetView();
  },

  computed: {
    isMain() {
      const testVal = this.$route.path.split("/");
      if (testVal[1] === "recipe") this.closeSidebar();
      else this.resetView();
      
      return !(testVal[1] === "admin");
    },
    customPages() {
      const pages = this.$store.getters.getCustomPages;
      if (pages.length > 0) {
        pages.sort((a, b) => a.position - b.position);
        return pages.map(x => ({
          title: x.name,
          to: `/pages/${x.slug}`,
          icon: "mdi-tag",
        }));
      } else {
        const categories = this.$store.getters.getAllCategories;
        return categories.map(x => ({
          title: x.name,
          to: `/recipes/category/${x.slug}`,
          icon: "mdi-tag",
        }));
      }
    },
    mainMenu() {
      return [...this.baseMainLinks, ...this.customPages];
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
  },

  methods: {
    resetView() {
      this.mobile = this.viewScale();
      this.showSidebar = !this.viewScale();
    },
    forceOpen() {
      this.showSidebar = !this.showSidebar;
    },
    closeSidebar() {
      this.showSidebar = !this.showSidebar;
    },
    viewScale() {
      switch (this.$vuetify.breakpoint.name) {
        case "xs":
          return true;
        case "sm":
          return true;
        default:
          return false;
      }
    },
    async getVersion() {
      let response = await axios.get(
        "https://api.github.com/repos/hay-kot/mealie/releases/latest",
        {
          headers: {
            "content-type": "application/json",
            Authorization: null,
          },
        }
      );

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
</style>