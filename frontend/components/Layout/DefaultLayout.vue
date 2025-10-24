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
      :secondary-links="cookbookLinks || []"
    >
      <v-menu
        offset-y
        nudge-bottom="5"
        close-delay="50"
        nudge-right="15"
      >
        <template #activator="{ props }">
          <v-btn
            v-if="isOwnGroup"
            rounded
            size="large"
            class="ml-2 mt-3"
            v-bind="props"
            variant="elevated"
            elevation="2"
            :color="$vuetify.theme.current.dark ? 'background-lighten-1' : 'background-darken-1'"
          >
            <v-icon
              start
              size="large"
              color="primary"
            >
              {{ $globals.icons.createAlt }}
            </v-icon>
            {{ $t("general.create") }}
          </v-btn>
        </template>
        <v-list
          density="comfortable"
          class="mb-0 mt-1 py-0"
          variant="flat"
        >
          <template v-for="(item, index) in createLinks">
            <div
              v-if="!item.hide"
              :key="item.title"
            >
              <v-divider
                v-if="item.insertDivider"
                :key="index"
                class="mx-2"
              />
              <v-list-item
                v-if="!item.restricted || isOwnGroup"
                :key="item.title"
                :to="item.to"
                exact
                class="my-1"
              >
                <template #prepend>
                  <v-icon
                    size="40"
                    :icon="item.icon"
                  />
                </template>
                <v-list-item-title class="font-weight-medium" style="font-size: small;">
                  {{ item.title }}
                </v-list-item-title>
                <v-list-item-subtitle class="font-weight-medium" style="font-size: small;">
                  {{ item.subtitle }}
                </v-list-item-subtitle>
              </v-list-item>
            </div>
          </template>
        </v-list>
      </v-menu>
    </AppSidebar>
    <v-main class="pt-12">
      <v-scroll-x-transition>
        <div>
          <NuxtPage />
        </div>
      </v-scroll-x-transition>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import type { SideBarLink } from "~/types/application-types";
import { useAppInfo } from "~/composables/api";
import { useCookbookPreferences } from "~/composables/use-users/preferences";
import { useCookbookStore, usePublicCookbookStore } from "~/composables/store/use-cookbook-store";
import type { ReadCookBook } from "~/lib/api/types/cookbook";

export default defineNuxtComponent({
  setup() {
    const i18n = useI18n();
    const { $globals } = useNuxtApp();
    const display = useDisplay();
    const $auth = useMealieAuth();
    const { isOwnGroup } = useLoggedInState();

    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");

    const cookbookPreferences = useCookbookPreferences();
    const ownCookbookStore = useCookbookStore(i18n);
    const publicCookbookStoreCache = ref<Record<string, ReturnType<typeof usePublicCookbookStore>>>({});

    function getPublicCookbookStore(slug: string) {
      if (!publicCookbookStoreCache.value[slug]) {
        publicCookbookStoreCache.value[slug] = usePublicCookbookStore(slug, i18n);
      }
      return publicCookbookStoreCache.value[slug];
    }

    const cookbooks = computed(() => {
      if (isOwnGroup.value) {
        return ownCookbookStore.store.value;
      }
      else if (groupSlug.value) {
        const publicStore = getPublicCookbookStore(groupSlug.value);
        return unref(publicStore.store);
      }
      return [];
    });

    const appInfo = useAppInfo();
    const showImageImport = computed(() => appInfo.value?.enableOpenaiImageServices);

    const languageDialog = ref<boolean>(false);

    const sidebar = ref<boolean>(false);
    onMounted(() => {
      sidebar.value = display.lgAndUp.value;
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

    const currentUserHouseholdId = computed(() => $auth.user.value?.householdId);
    const cookbookLinks = computed<SideBarLink[]>(() => {
      if (!cookbooks.value?.length) {
        return [];
      }

      const sortedCookbooks = [...cookbooks.value].sort((a, b) => (a.position || 0) - (b.position || 0));

      const ownLinks: SideBarLink[] = [];
      const links: SideBarLink[] = [];
      const cookbooksByHousehold = sortedCookbooks.reduce((acc, cookbook) => {
        const householdName = cookbook.household?.name || "";
        (acc[householdName] ||= []).push(cookbook);
        return acc;
      }, {} as Record<string, ReadCookBook[]>);

      Object.entries(cookbooksByHousehold).forEach(([householdName, cookbooks]) => {
        if (!cookbooks.length) {
          return;
        }
        if (cookbooks[0].householdId === currentUserHouseholdId.value) {
          ownLinks.push(...cookbooks.map(cookbookAsLink));
        }
        else {
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
      if ($auth.user.value && cookbookPreferences.value.hideOtherHouseholds) {
        return ownLinks;
      }
      else {
        return [...ownLinks, ...links];
      }
    });

    const createLinks = computed(() => [
      {
        insertDivider: false,
        icon: $globals.icons.link,
        title: i18n.t("general.import"),
        subtitle: i18n.t("new-recipe.import-by-url"),
        to: `/g/${groupSlug.value}/r/create/url`,
        restricted: true,
        hide: false,
      },
      {
        insertDivider: false,
        icon: $globals.icons.fileImage,
        title: i18n.t("recipe.create-from-images"),
        subtitle: i18n.t("recipe.create-recipe-from-an-image"),
        to: `/g/${groupSlug.value}/r/create/image`,
        restricted: true,
        hide: !showImageImport.value,
      },
      {
        insertDivider: true,
        icon: $globals.icons.edit,
        title: i18n.t("general.create"),
        subtitle: i18n.t("new-recipe.create-manually"),
        to: `/g/${groupSlug.value}/r/create/new`,
        restricted: true,
        hide: false,
      },
    ]);

    const topLinks = computed<SideBarLink[]>(() => [
      {
        icon: $globals.icons.silverwareForkKnife,
        to: `/g/${groupSlug.value}`,
        title: i18n.t("general.recipes"),
        restricted: false,
      },
      {
        icon: $globals.icons.search,
        to: `/g/${groupSlug.value}/recipes/finder`,
        title: i18n.t("recipe-finder.recipe-finder"),
        restricted: false,
      },
      {
        icon: $globals.icons.calendarMultiselect,
        title: i18n.t("meal-plan.meal-planner"),
        to: "/household/mealplan/planner/view",
        restricted: true,
      },
      {
        icon: $globals.icons.formatListCheck,
        title: i18n.t("shopping-list.shopping-lists"),
        to: "/shopping-lists",
        restricted: true,
      },
      {
        icon: $globals.icons.timelineText,
        title: i18n.t("recipe.timeline"),
        to: `/g/${groupSlug.value}/recipes/timeline`,
        restricted: true,
      },
      {
        icon: $globals.icons.book,
        to: `/g/${groupSlug.value}/cookbooks`,
        title: i18n.t("cookbook.cookbooks"),
        restricted: true,
      },
      {
        icon: $globals.icons.organizers,
        title: i18n.t("general.organizers"),
        restricted: true,
        children: [
          {
            icon: $globals.icons.categories,
            to: `/g/${groupSlug.value}/recipes/categories`,
            title: i18n.t("sidebar.categories"),
            restricted: true,
          },
          {
            icon: $globals.icons.tags,
            to: `/g/${groupSlug.value}/recipes/tags`,
            title: i18n.t("sidebar.tags"),
            restricted: true,
          },
          {
            icon: $globals.icons.potSteam,
            to: `/g/${groupSlug.value}/recipes/tools`,
            title: i18n.t("tool.tools"),
            restricted: true,
          },
        ],
      },
    ]);

    return {
      groupSlug,
      cookbookLinks,
      createLinks,
      topLinks,
      isOwnGroup,
      languageDialog,
      sidebar,
    };
  },
});
</script>
