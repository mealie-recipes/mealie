<template>
  <v-app dark>
    <TheSnackbar />

    <AppSidebar
      v-model="sidebar"
      absolute
      :top-link="topLinks"
      :secondary-links="cookbookLinks || []"
      :bottom-links="isAdmin ? bottomLinks : []"
    >
      <v-menu offset-y nudge-bottom="5" close-delay="50" nudge-right="15">
        <template #activator="{ on, attrs }">
          <v-btn v-if="isOwnGroup" rounded large class="ml-2 mt-3" v-bind="attrs" v-on="on">
            <v-icon left large color="primary">
              {{ $globals.icons.createAlt }}
            </v-icon>
            {{ $t("general.create") }}
          </v-btn>
        </template>
        <v-list dense class="my-0 py-0">
          <template v-for="(item, index) in createLinks">
            <div v-if="!item.hide" :key="item.title">
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
            </div>
          </template>
        </v-list>
      </v-menu>
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
import { SideBarLink } from "~/types/application-types";
import LanguageDialog from "~/components/global/LanguageDialog.vue";
import TheSnackbar from "@/components/Layout/LayoutParts/TheSnackbar.vue";
import { useAppInfo } from "~/composables/api";
import { useCookbooks, usePublicCookbooks } from "~/composables/use-group-cookbooks";
import { useCookbookPreferences } from "~/composables/use-users/preferences";
import { useHouseholdStore, usePublicHouseholdStore } from "~/composables/store/use-household-store";
import { useToggleDarkMode } from "~/composables/use-utils";
import { ReadCookBook } from "~/lib/api/types/cookbook";
import { HouseholdSummary } from "~/lib/api/types/household";


export default defineComponent({
  components: { AppHeader, AppSidebar, LanguageDialog, TheSnackbar },
  setup() {
    const { $globals, $auth, $vuetify, i18n } = useContext();
    const { isOwnGroup } = useLoggedInState();

    const isAdmin = computed(() => $auth.user?.admin);
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");
    const { cookbooks } = isOwnGroup.value ? useCookbooks() : usePublicCookbooks(groupSlug.value || "");
    const cookbookPreferences = useCookbookPreferences();
    const { store: households } = isOwnGroup.value ? useHouseholdStore() : usePublicHouseholdStore(groupSlug.value || "");

    const householdsById = computed(() => {
      return households.value.reduce((acc, household) => {
        acc[household.id] = household;
        return acc;
      }, {} as { [key: string]: HouseholdSummary });
    });

    const appInfo = useAppInfo();
    const showImageImport = computed(() => appInfo.value?.enableOpenaiImageServices);

    const toggleDark = useToggleDarkMode();

    const languageDialog = ref<boolean>(false);

    const sidebar = ref<boolean | null>(null);

    onMounted(() => {
      sidebar.value = !$vuetify.breakpoint.md;
    });

    function cookbookAsLink(cookbook: ReadCookBook): SideBarLink {
      return {
        key: cookbook.slug || "",
        icon: $globals.icons.pages,
        title: cookbook.name,
        to: `/g/${groupSlug.value}/cookbooks/${cookbook.slug || ""}`,
        restricted: false,
      };
    }

    const currentUserHouseholdId = computed(() => $auth.user?.householdId);
    const cookbookLinks = computed<SideBarLink[]>(() => {
      if (!cookbooks.value) {
        return [];
      }
      cookbooks.value.sort((a, b) => (a.position || 0) - (b.position || 0));

      const ownLinks: SideBarLink[] = [];
      const links: SideBarLink[] = [];
      const cookbooksByHousehold = cookbooks.value.reduce((acc, cookbook) => {
        const householdName = householdsById.value[cookbook.householdId]?.name || "";
        if (!acc[householdName]) {
          acc[householdName] = [];
        }
        acc[householdName].push(cookbook);
        return acc;
      }, {} as Record<string, ReadCookBook[]>);

      Object.entries(cookbooksByHousehold).forEach(([householdName, cookbooks]) => {
        if (cookbooks[0].householdId === currentUserHouseholdId.value) {
          ownLinks.push(...cookbooks.map(cookbookAsLink));
        } else {
          links.push({
            key: householdName,
            icon: $globals.icons.book,
            title: householdName,
            children: cookbooks.map(cookbookAsLink),
            restricted: false,
          });
        }
      });

      links.sort((a, b) => a.title.localeCompare(b.title));
      if ($auth.user && cookbookPreferences.value.hideOtherHouseholds) {
        return ownLinks;
      } else {
        return [...ownLinks, ...links];
      }
    });

    const createLinks = computed<SideBarLink[]>(() => [
      {
        insertDivider: false,
        icon: $globals.icons.link,
        title: i18n.tc("general.import"),
        subtitle: i18n.tc("new-recipe.import-by-url"),
        to: `/g/${groupSlug.value}/r/create/url`,
        restricted: true,
        hide: false,
      },
      {
        insertDivider: false,
        icon: $globals.icons.fileImage,
        title: i18n.tc("recipe.create-from-image"),
        subtitle: i18n.tc("recipe.create-recipe-from-an-image"),
        to: `/g/${groupSlug.value}/r/create/image`,
        restricted: true,
        hide: !showImageImport.value,
      },
      {
        insertDivider: true,
        icon: $globals.icons.edit,
        title: i18n.tc("general.create"),
        subtitle: i18n.tc("new-recipe.create-manually"),
        to: `/g/${groupSlug.value}/r/create/new`,
        restricted: true,
        hide: false,
      },
    ]);

    const bottomLinks = computed<SideBarLink[]>(() => [
      {
        icon: $globals.icons.cog,
        title: i18n.tc("general.settings"),
        to: "/admin/site-settings",
        restricted: true,
      },
    ]);

    const topLinks = computed<SideBarLink[]>(() => [
      {
        icon: $globals.icons.silverwareForkKnife,
        to: `/g/${groupSlug.value}`,
        title: i18n.tc("general.recipes"),
        restricted: false,
      },
      {
        icon: $globals.icons.search,
        to: `/g/${groupSlug.value}/recipes/finder`,
        title: i18n.tc("recipe-finder.recipe-finder"),
        restricted: false,
      },
      {
        icon: $globals.icons.calendarMultiselect,
        title: i18n.tc("meal-plan.meal-planner"),
        to: "/household/mealplan/planner/view",
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
        icon: $globals.icons.book,
        to: `/g/${groupSlug.value}/cookbooks`,
        title: i18n.tc("cookbook.cookbooks"),
        restricted: true,
      },
      {
        icon: $globals.icons.organizers,
        title: i18n.tc("general.organizers"),
        restricted: true,
        children: [
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
        ],
      },
    ]);

    return {
      groupSlug,
      cookbookLinks,
      createLinks,
      bottomLinks,
      topLinks,
      isAdmin,
      isOwnGroup,
      languageDialog,
      toggleDark,
      sidebar,
    };
  },
});
</script>
