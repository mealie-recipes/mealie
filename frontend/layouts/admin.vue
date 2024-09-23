<template>
  <v-app dark>
    <AppSidebar
      v-model="sidebar"
      absolute
      :top-link="topLinks"
      :bottom-links="bottomLinks"
      :user="{ data: true }"
      :secondary-header="$t('sidebar.developer')"
      :secondary-links="developerLinks"
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
import AppHeader from "@/components/Layout/LayoutParts/AppHeader.vue";
import AppSidebar from "@/components/Layout/LayoutParts/AppSidebar.vue";
import TheSnackbar from "~/components/Layout/LayoutParts/TheSnackbar.vue";
import { SidebarLinks } from "~/types/application-types";

export default defineComponent({
  components: { AppHeader, AppSidebar, TheSnackbar },
  middleware: ["auth", "admin-only"],
  auth: true,
  setup() {
    const { $globals, i18n, $vuetify } = useContext();

    const sidebar = ref<boolean | null>(null);
    onMounted(() => {
      sidebar.value = !$vuetify.breakpoint.md;
    });

    const topLinks: SidebarLinks = [
      {
        icon: $globals.icons.cog,
        to: "/admin/site-settings",
        title: i18n.tc("sidebar.site-settings"),
        restricted: true,
      },

      // {
      //   icon: $globals.icons.chart,
      //   to: "/admin/analytics",
      //   title: "Analytics",
      //   restricted: true,
      // },
      {
        icon: $globals.icons.user,
        to: "/admin/manage/users",
        title: i18n.tc("user.users"),
        restricted: true,
      },
      {
        icon: $globals.icons.household,
        to: "/admin/manage/households",
        title: i18n.tc("household.households"),
        restricted: true,
      },
      {
        icon: $globals.icons.group,
        to: "/admin/manage/groups",
        title: i18n.tc("group.groups"),
        restricted: true,
      },
      {
        icon: $globals.icons.database,
        to: "/admin/backups",
        title: i18n.tc("sidebar.backups"),
        restricted: true,
      },
    ];

    const developerLinks: SidebarLinks = [
      {
        icon: $globals.icons.wrench,
        to: "/admin/maintenance",
        title: i18n.tc("sidebar.maintenance"),
        restricted: true,
      },
      {
        icon: $globals.icons.robot,
        title: i18n.tc("recipe.debug"),
        restricted: true,
        children: [
          {
            icon: $globals.icons.robot,
            to: "/admin/debug/openai",
            title: i18n.tc("admin.openai"),
            restricted: true,
          },
          {
            icon: $globals.icons.slotMachine,
            to: "/admin/debug/parser",
            title: i18n.tc("sidebar.parser"),
            restricted: true,
          },
        ]
      },
    ];

    const bottomLinks: SidebarLinks = [
      {
        icon: $globals.icons.heart,
        title: i18n.tc("about.support"),
        href: "https://github.com/sponsors/hay-kot",
        restricted: true,
      },
    ];

    return {
      sidebar,
      topLinks,
      bottomLinks,
      developerLinks,
    };
  },
});
</script>
