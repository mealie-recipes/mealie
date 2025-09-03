<template>
  <v-app dark>
    <TheSnackbar />

    <AppHeader>
      <v-btn
        icon
        @click.stop="sidebar = !sidebar"
      >
        <v-icon> {{ $globals.icons.menu }}</v-icon>
      </v-btn>
    </AppHeader>

    <AppSidebar
      v-model="sidebar"
      absolute
      :top-link="topLinks"
      :bottom-links="bottomLinks"
      :user="{ data: true }"
      :secondary-header="$t('sidebar.developer')"
      :secondary-links="developerLinks"
    />

    <v-main>
      <v-scroll-x-transition>
        <div>
          <NuxtPage />
        </div>
      </v-scroll-x-transition>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import AppHeader from "@/components/Layout/LayoutParts/AppHeader.vue";
import AppSidebar from "@/components/Layout/LayoutParts/AppSidebar.vue";
import TheSnackbar from "~/components/Layout/LayoutParts/TheSnackbar.vue";
import type { SidebarLinks } from "~/types/application-types";
import { useGlobalI18n } from "~/composables/use-global-i18n";

const i18n = useGlobalI18n();
const display = useDisplay();
const { $globals } = useNuxtApp();

const sidebar = ref<boolean>(false);
onMounted(() => {
  sidebar.value = !display.md.value;
});

const topLinks: SidebarLinks = [
  {
    icon: $globals.icons.cog,
    to: "/admin/site-settings",
    title: i18n.t("sidebar.site-settings"),
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
    title: i18n.t("user.users"),
    restricted: true,
  },
  {
    icon: $globals.icons.household,
    to: "/admin/manage/households",
    title: i18n.t("household.households"),
    restricted: true,
  },
  {
    icon: $globals.icons.group,
    to: "/admin/manage/groups",
    title: i18n.t("group.groups"),
    restricted: true,
  },
  {
    icon: $globals.icons.database,
    to: "/admin/backups",
    title: i18n.t("sidebar.backups"),
    restricted: true,
  },
];

const developerLinks: SidebarLinks = [
  {
    icon: $globals.icons.wrench,
    to: "/admin/maintenance",
    title: i18n.t("sidebar.maintenance"),
    restricted: true,
  },
  {
    icon: $globals.icons.robot,
    title: i18n.t("recipe.debug"),
    restricted: true,
    children: [
      {
        icon: $globals.icons.robot,
        to: "/admin/debug/openai",
        title: i18n.t("admin.openai"),
        restricted: true,
      },
      {
        icon: $globals.icons.slotMachine,
        to: "/admin/debug/parser",
        title: i18n.t("sidebar.parser"),
        restricted: true,
      },
    ],
  },
];

const bottomLinks: SidebarLinks = [
  {
    icon: $globals.icons.heart,
    title: i18n.t("about.support"),
    href: "https://github.com/sponsors/hay-kot",
    restricted: true,
  },
];
</script>
