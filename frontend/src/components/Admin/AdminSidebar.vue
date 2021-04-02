<template>
  <div>
    <v-btn
      class="mt-9 ml-n1"
      fixed
      left
      bottom
      fab
      small
      color="primary"
      @click="showSidebar = !showSidebar"
    >
      <v-icon>mdi-cog</v-icon></v-btn
    >

    <v-navigation-drawer
      :value="mobile ? showSidebar : true"
      v-model="showSidebar"
      width="180px"
      clipped
      app
    >
      <template v-slot:prepend>
        <v-list-item two-line>
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
          v-for="nav in baseLinks"
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

      <v-divider></v-divider>
      <v-list nav dense v-if="user.admin">
        <v-list-item
          v-for="nav in superLinks"
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

      <v-list nav dense class="fixedBottom">
        <v-list-item href="">
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
import { validators } from "@/mixins/validators";
import { initials } from "@/mixins/initials";
import { user } from "@/mixins/user";
import axios from "axios";
export default {
  mixins: [validators, initials, user],
  data() {
    return {
      latestVersion: null,
      hideImage: false,
      showSidebar: false,
      mobile: false,
      links: [],
      superLinks: [
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
      baseLinks: [
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
    };
  },
  async mounted() {
    this.mobile = this.viewScale();
    this.showSidebar = !this.viewScale();
    this.getVersion();
  },

  computed: {
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
  },

  methods: {
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