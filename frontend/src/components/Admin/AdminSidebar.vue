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
          <v-list-item-avatar>
            <img src="https://randomuser.me/api/portraits/women/81.jpg" />
          </v-list-item-avatar>

          <v-list-item-content>
            <v-list-item-title>Jane Smith</v-list-item-title>
            <v-list-item-subtitle>Admin</v-list-item-subtitle>
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
      <v-list nav dense>
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
    </v-navigation-drawer>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showSidebar: false,
      mobile: false,
      links: [],
      superLinks: [
        {
          icon: "mdi-account-group",
          to: "/admin/manage-users",
          title: "Manage Users",
        },
        {
          icon: "mdi-cog",
          to: "/admin/settings",
          title: "Admin Settings",
        },
      ],
      baseLinks: [
        {
          icon: "mdi-account",
          to: "/admin/profile",
          title: "Profile",
        },
        {
          icon: "mdi-card-bulleted-settings-outline",
          to: "/admin/general",
          title: "General",
        },
        {
          icon: "mdi-format-color-fill",
          to: "/admin/themes",
          title: "Themes",
        },
        {
          icon: "mdi-food",
          to: "/admin/meal-planner",
          title: "Meal Planner",
        },
        {
          icon: "mdi-backup-restore",
          to: "/admin/backups",
          title: "Backups",
        },
        {
          icon: "mdi-database-import",
          to: "/admin/migrations",
          title: "Migrations",
        },
      ],
    };
  },
  mounted() {
    this.mobile = this.viewScale();
    this.showSidebar = !this.viewScale();
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
  },
};
</script>

<style>
</style>