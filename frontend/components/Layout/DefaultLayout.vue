<template>
    <v-app dark>
      <TheSnackbar />

      <AppSidebar
        v-model="sidebar"
        absolute
        :top-link="topLinks"
        :secondary-header="cookbookLinks.length ? $tc('sidebar.cookbooks') : undefined"
        :secondary-header-link="isOwnGroup && cookbookLinks.length ? `/g/${groupSlug}/cookbooks` : undefined"
        :secondary-links="cookbookLinks || []"
        :bottom-links="isAdmin ? bottomLinks : []"
      >
        <v-menu offset-y nudge-bottom="5" close-delay="50" nudge-right="15">
          <template #activator="{ on, attrs }">
            <v-btn v-if="loggedIn" rounded large class="ml-2 mt-3" v-bind="attrs" v-on="on">
              <v-icon left large color="primary">
                {{ $globals.icons.createAlt }}
              </v-icon>
              {{ $t("general.create") }}
            </v-btn>
          </template>
          <v-list dense class="my-0 py-0">
            <template v-for="(item, index) in createLinks">
              <v-divider v-if="item.insertDivider" :key="index" class="mx-2"></v-divider>
              <v-list-item v-if="!item.restricted || isOwnGroup" :key="item.title" :to="item.to" exact>
                <v-list-item-avatar>
                  <v-icon>
                    {{ item.icon }}
                  </v-icon>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>
                    {{ item.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle v-if="item.subtitle">
                    {{ item.subtitle }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </template>
          </v-list>
        </v-menu>
        <template v-if="groupLinks" #groups>
          <v-subheader class="pb-0">
            {{ $t("sidebar.groups") }}
          </v-subheader>
          <v-divider></v-divider>
          <v-list nav dense exact>
            <template v-for="nav in groupLinks">
              <div :key="nav.title">
                <v-list-item-group :key="nav.title + 'single-item'" color="primary">
                  <v-list-item exact link :to="nav.to">
                    <v-list-item-icon>
                      <v-icon>{{ nav.icon }}</v-icon>
                    </v-list-item-icon>
                    <v-list-item-title>{{ nav.title }}</v-list-item-title>
                  </v-list-item>
                </v-list-item-group>
              </div>
            </template>
          </v-list>
        </template>
        <template #bottom>
          <v-list-item @click.stop="languageDialog = true">
            <v-list-item-icon>
              <v-icon>{{ $globals.icons.translate }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{ $t("sidebar.language") }}</v-list-item-title>
              <LanguageDialog v-model="languageDialog" />
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="toggleDark">
            <v-list-item-icon>
              <v-icon>
                {{ $vuetify.theme.dark ? $globals.icons.weatherSunny : $globals.icons.weatherNight }}
              </v-icon>
            </v-list-item-icon>
            <v-list-item-title>
              {{ $vuetify.theme.dark ? $t("settings.theme.light-mode") : $t("settings.theme.dark-mode") }}
            </v-list-item-title>
          </v-list-item>
        </template>
      </AppSidebar>

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
  import { computed, defineComponent, onMounted, ref, useContext, useRoute } from "@nuxtjs/composition-api";
  import { useLoggedInState } from "~/composables/use-logged-in-state";
  import AppHeader from "@/components/Layout/LayoutParts/AppHeader.vue";
  import AppSidebar from "@/components/Layout/LayoutParts/AppSidebar.vue";
  import { SidebarLinks } from "~/types/application-types";
  import LanguageDialog from "~/components/global/LanguageDialog.vue";
  import TheSnackbar from "@/components/Layout/LayoutParts/TheSnackbar.vue";
  import { useCookbooks, usePublicCookbooks } from "~/composables/use-group-cookbooks";
  import { usePublicGroups } from "~/composables/use-groups";
  import { useToggleDarkMode } from "~/composables/use-utils";

  export default defineComponent({
    components: { AppHeader, AppSidebar, LanguageDialog, TheSnackbar },
    setup() {
      const { $globals, $auth, $vuetify, i18n } = useContext();
      const { loggedIn, isOwnGroup } = useLoggedInState();
      const { groups } = usePublicGroups();

      const isAdmin = computed(() => $auth.user?.admin);
      const route = useRoute();
      const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");
      const userGroupSlug = computed(() => $auth.user?.groupSlug || "");

      const toggleDark = useToggleDarkMode();

      const languageDialog = ref<boolean>(false);

      const sidebar = ref<boolean | null>(null);

      onMounted(() => {
        sidebar.value = !$vuetify.breakpoint.md;
      });

      const groupLinks = computed(() => {
        if (!groups.value) return null;
        return groups.value?.filter(group => group.slug !== groupSlug.value).map((group) => {
          return {
            icon: $globals.icons.group,
            title: group.name,
            to: `/g/${group.slug}`,
          };
        });
      });

      const cookbookLinks = computed(() => {
        const { cookbooks } = isOwnGroup.value ? useCookbooks() : usePublicCookbooks(groupSlug.value || "");
        if (!cookbooks.value) return [];
        return cookbooks.value.map((cookbook) => {
          return {
            icon: $globals.icons.pages,
            title: cookbook.name,
            to: `/g/${groupSlug.value}/cookbooks/${cookbook.slug as string}`,
          };
        });
      });

      interface Link {
        insertDivider: boolean;
        icon: string;
        title: string;
        subtitle: string | null;
        to: string;
        restricted: boolean;
      }

      const createLinks = computed<Link[]>(() => [
        {
          insertDivider: false,
          icon: $globals.icons.link,
          title: i18n.tc("general.import"),
          subtitle: i18n.tc("new-recipe.import-by-url"),
          to: `/g/${userGroupSlug.value}/r/create/url`,
          restricted: !loggedIn.value,
        },
        {
          insertDivider: true,
          icon: $globals.icons.edit,
          title: i18n.tc("general.create"),
          subtitle: i18n.tc("new-recipe.create-manually"),
          to: `/g/${userGroupSlug.value}/r/create/new`,
          restricted: !loggedIn.value,
        },
        {
          insertDivider: true,
          icon: $globals.icons.pages,
          title: i18n.tc("sidebar.cookbook"),
          subtitle: i18n.tc("sidebar.create-cookbook"),
          to: `/g/${userGroupSlug.value}/cookbooks`,
          restricted: !loggedIn.value,
        },
      ]);

      const bottomLinks = computed<SidebarLinks>(() => [
        {
          icon: $globals.icons.cog,
          title: i18n.tc("general.settings"),
          to: "/admin/site-settings",
          restricted: !isAdmin.value,
        },
      ]);

      const topLinks = computed<SidebarLinks>(() => [
        {
          icon: $globals.icons.search,
          to: `/g/${groupSlug.value}`,
          title: i18n.tc("sidebar.search"),
          restricted: false,
        },
        {
          icon: $globals.icons.calendarMultiselect,
          title: i18n.tc("meal-plan.meal-planner"),
          to: "/group/mealplan/planner/view",
          restricted: true,
        },
        {
          icon: $globals.icons.formatListCheck,
          title: i18n.tc("shopping-list.shopping-lists"),
          to: "/shopping-lists",
          restricted: true,
        },
        {
          icon: $globals.icons.timelineText,
          title: i18n.tc("recipe.timeline"),
          to: `/g/${groupSlug.value}/recipes/timeline`,
          restricted: true,
        },
        {
          icon: $globals.icons.categories,
          to: `/g/${groupSlug.value}/recipes/categories`,
          title: i18n.tc("sidebar.categories"),
          restricted: true,
        },
        {
          icon: $globals.icons.tags,
          to: `/g/${groupSlug.value}/recipes/tags`,
          title: i18n.tc("sidebar.tags"),
          restricted: true,
        },
        {
          icon: $globals.icons.potSteam,
          to: `/g/${groupSlug.value}/recipes/tools`,
          title: i18n.tc("tool.tools"),
          restricted: true,
        },
      ]);

      return {
        groupSlug,
        groupLinks,
        cookbookLinks,
        createLinks,
        bottomLinks,
        topLinks,
        loggedIn,
        isAdmin,
        isOwnGroup,
        languageDialog,
        toggleDark,
        sidebar,
      };
    },
  });
  </script>
