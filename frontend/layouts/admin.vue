<template>
  <v-app dark>
    <AppSidebar
      v-model="sidebar"
      absolute
      :top-link="topLinks"
      :bottom-links="bottomLinks"
      :user="{ data: true }"
      :secondary-header="$t('user.admin')"
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
import { SidebarLinks } from "~/types/application-types";

export default defineComponent({
  components: { AppHeader, AppSidebar, TheSnackbar },
  middleware: "auth",
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
        title: i18n.t("sidebar.site-settings"),
      },
      {
        icon: $globals.icons.wrench,
        to: "/admin/maintenance",
        title: "Maintenance",
      },
      {
        icon: $globals.icons.chart,
        to: "/admin/analytics",
        title: "Analytics",
      },
      {
        icon: $globals.icons.user,
        to: "/admin/manage/users",
        title: i18n.t("user.users"),
      },
      {
        icon: $globals.icons.group,
        to: "/admin/manage/groups",
        title: i18n.t("group.groups"),
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

    const bottomLinks: SidebarLinks = [
      {
        icon: $globals.icons.heart,
        title: i18n.t("about.support"),
        href: "https://github.com/sponsors/hay-kot",
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
