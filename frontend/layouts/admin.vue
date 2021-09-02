<template>
  <v-app dark>
    <!-- <TheSnackbar /> -->

    <AppSidebar
      v-model="sidebar"
      absolute
      :top-link="topLinks"
      :secondary-links="$auth.user.admin ? adminLinks : null"
      :bottom-links="$auth.user.admin ? bottomLinks : null"
      :user="{ data: true }"
      :secondary-header="$t('user.admin')"
      @input="sidebar = !sidebar"
    />

    <TheSnackbar />

    <AppHeader>
      <v-btn icon @click.stop="sidebar = !sidebar">
        <v-icon> {{ $globals.icons.menu }}</v-icon>
      </v-btn>
    </AppHeader>
    <v-main>
      <v-scroll-x-transition>
        <Nuxt />
      </v-scroll-x-transition>
    </v-main>
  </v-app>
</template>
  

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import AppHeader from "@/components/Layout/AppHeader.vue";
import AppSidebar from "@/components/Layout/AppSidebar.vue";
import TheSnackbar from "~/components/Layout/TheSnackbar.vue";

export default defineComponent({
  components: { AppHeader, AppSidebar, TheSnackbar },
  middleware: "auth",
  auth: true,
  setup() {
    return {};
  },
  data() {
    return {
      sidebar: null,
      topLinks: [
        {
          icon: this.$globals.icons.user,
          to: "/user/profile",
          title: this.$t("sidebar.profile"),
        },
        {
          icon: this.$globals.icons.group,
          to: "/user/group",
          title: this.$t("group.group"),
        },
        {
          icon: this.$globals.icons.pages,
          to: "/user/group/cookbooks",
          title: this.$t("sidebar.cookbooks"),
        },
        {
          icon: this.$globals.icons.webhook,
          to: "/user/group/webhooks",
          title: "Webhooks",
        },
      ],
      adminLinks: [
        {
          icon: this.$globals.icons.viewDashboard,
          to: "/admin/dashboard",
          title: this.$t("sidebar.dashboard"),
        },
        {
          icon: this.$globals.icons.cog,
          to: "/admin/site-settings",
          title: this.$t("sidebar.site-settings"),
        },
        {
          icon: this.$globals.icons.tools,
          to: "/admin/toolbox",
          title: this.$t("sidebar.toolbox"),
          children: [
            {
              icon: this.$globals.icons.bellAlert,
              to: "/admin/toolbox/notifications",
              title: this.$t("events.notification"),
            },
            {
              icon: this.$globals.icons.foods,
              to: "/admin/toolbox/foods",
              title: "Manage Foods",
            },
            {
              icon: this.$globals.icons.units,
              to: "/admin/toolbox/units",
              title: "Manage Units",
            },
            {
              icon: this.$globals.icons.tags,
              to: "/admin/toolbox/categories",
              title: this.$t("sidebar.tags"),
            },
            {
              icon: this.$globals.icons.tags,
              to: "/admin/toolbox/tags",
              title: this.$t("sidebar.categories"),
            },
            {
              icon: this.$globals.icons.broom,
              to: "/admin/toolbox/organize",
              title: this.$t("settings.organize"),
            },
          ],
        },
        {
          icon: this.$globals.icons.group,
          to: "/admin/manage-users",
          title: this.$t("sidebar.manage-users"),
          children: [
            {
              icon: this.$globals.icons.user,
              to: "/admin/manage-users/all-users",
              title: this.$t("user.users"),
            },
            {
              icon: this.$globals.icons.group,
              to: "/admin/manage-users/all-groups",
              title: this.$t("group.groups"),
            },
          ],
        },
        {
          icon: this.$globals.icons.import,
          to: "/admin/migrations",
          title: this.$t("sidebar.migrations"),
        },
        {
          icon: this.$globals.icons.database,
          to: "/admin/backups",
          title: this.$t("sidebar.backups"),
        },
      ],
      bottomLinks: [
        {
          icon: this.$globals.icons.heart,
          title: this.$t("about.support"),
          href: "https://github.com/sponsors/hay-kot",
        },
        {
          icon: this.$globals.icons.information,
          title: this.$t("about.about"),
          to: "/admin/about",
        },
      ],
    };
  },
  head: {
    title: "Admin",
  },
});
</script>
      
      <style scoped>
</style>+