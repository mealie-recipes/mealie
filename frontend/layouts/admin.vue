<template>
  <v-app dark>
    <AppSidebar
      v-model="sidebar"
      absolute
      :top-link="topLinks"
      :bottom-links="bottomLinks"
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
import { defineComponent, ref, useContext, onMounted } from "@nuxtjs/composition-api";
import AppHeader from "@/components/Layout/AppHeader.vue";
import AppSidebar from "@/components/Layout/AppSidebar.vue";
import TheSnackbar from "~/components/Layout/TheSnackbar.vue";

export default defineComponent({
  components: { AppHeader, AppSidebar, TheSnackbar },
  middleware: "auth",
  auth: true,
  setup() {
    // @ts-ignore - $globals not found in type definition
    const { $globals, i18n, $vuetify } = useContext();

    const sidebar = ref<boolean | null>(null);
    onMounted(() => {
      sidebar.value = !$vuetify.breakpoint.md;
    });

    const topLinks = [
      {
        icon: $globals.icons.viewDashboard,
        to: "/admin/dashboard",
        title: i18n.t("sidebar.dashboard"),
      },
      {
        icon: $globals.icons.cog,
        to: "/admin/site-settings",
        title: i18n.t("sidebar.site-settings"),
      },
      {
        icon: $globals.icons.tools,
        to: "/admin/toolbox",
        title: i18n.t("sidebar.toolbox"),
        children: [
          {
            icon: $globals.icons.bellAlert,
            to: "/admin/toolbox/notifications",
            title: i18n.t("events.notification"),
          },
          {
            icon: $globals.icons.foods,
            to: "/admin/toolbox/foods",
            title: "Manage Foods",
          },
          {
            icon: $globals.icons.units,
            to: "/admin/toolbox/units",
            title: "Manage Units",
          },
          {
            icon: $globals.icons.tags,
            to: "/admin/toolbox/categories",
            title: i18n.t("sidebar.tags"),
          },
          {
            icon: $globals.icons.tags,
            to: "/admin/toolbox/tags",
            title: i18n.t("sidebar.categories"),
          },
        ],
      },
      {
        icon: $globals.icons.group,
        to: "/admin/manage-users",
        title: i18n.t("sidebar.manage-users"),
        children: [
          {
            icon: $globals.icons.user,
            to: "/admin/manage-users/all-users",
            title: i18n.t("user.users"),
          },
          {
            icon: $globals.icons.group,
            to: "/admin/manage-users/all-groups",
            title: i18n.t("group.groups"),
          },
        ],
      },
      {
        icon: $globals.icons.import,
        to: "/admin/migrations",
        title: i18n.t("sidebar.migrations"),
      },
      {
        icon: $globals.icons.database,
        to: "/admin/backups",
        title: i18n.t("sidebar.backups"),
      },
      {
        icon: $globals.icons.check,
        to: "/admin/background-tasks",
        title: "Background Tasks",
      },
      {
        icon: $globals.icons.slotMachine,
        to: "/admin/parser",
        title: "Parser",
      },
    ];

    const bottomLinks = [
      {
        icon: $globals.icons.heart,
        title: i18n.t("about.support"),
        href: "https://github.com/sponsors/hay-kot",
      },
      {
        icon: $globals.icons.information,
        title: i18n.t("about.about"),
        to: "/admin/about",
      },
    ];

    return {
      sidebar,
      topLinks,
      bottomLinks,
    };
  },
});
</script>



    