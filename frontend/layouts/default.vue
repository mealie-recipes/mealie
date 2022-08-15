<template>
  <v-app dark>
    <TheSnackbar />

    <AppSidebar
      v-model="sidebar"
      absolute
      :top-link="topLinks"
      :secondary-header="$t('sidebar.cookbooks')"
      secondary-header-link="/group/cookbooks"
      :secondary-links="cookbookLinks || []"
      :bottom-links="isAdmin ? bottomLink : []"
    >
      <v-menu offset-y nudge-bottom="5" close-delay="50" nudge-right="15">
        <template #activator="{ on, attrs }">
          <v-btn rounded large class="ml-2 mt-3" v-bind="attrs" v-on="on">
            <v-icon left large color="primary">
              {{ $globals.icons.createAlt }}
            </v-icon>
            {{ $t("general.create") }}
          </v-btn>
        </template>
        <v-list dense class="my-0 py-0">
          <template v-for="(item, index) in createLinks">
            <v-divider v-if="item.divider" :key="index" class="mx-2"></v-divider>
            <v-list-item v-else :key="item.title" :to="item.to" exact>
              <v-list-item-avatar>
                <v-icon>
                  {{ item.icon }}
                </v-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>
                  {{ item.title }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ item.subtitle }}
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
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
import { computed, defineComponent, onMounted, ref, useContext } from "@nuxtjs/composition-api";
import AppHeader from "@/components/Layout/AppHeader.vue";
import AppSidebar from "@/components/Layout/AppSidebar.vue";
import LanguageDialog from "~/components/global/LanguageDialog.vue";
import TheSnackbar from "@/components/Layout/TheSnackbar.vue";
import { useCookbooks } from "~/composables/use-group-cookbooks";
import { useToggleDarkMode } from "~/composables/use-utils";

export default defineComponent({
  components: { AppHeader, AppSidebar, LanguageDialog, TheSnackbar },
  middleware: "auth",
  setup() {
    const { cookbooks } = useCookbooks();
    const { $globals, $auth, $vuetify, i18n } = useContext();

    const isAdmin = computed(() => $auth.user?.admin);

    const toggleDark = useToggleDarkMode();

    const languageDialog = ref<boolean>(false);

    const sidebar = ref<boolean | null>(null);

    onMounted(() => {
      sidebar.value = !$vuetify.breakpoint.md;
    });

    const cookbookLinks = computed(() => {
      if (!cookbooks.value) return [];
      return cookbooks.value.map((cookbook) => {
        return {
          icon: $globals.icons.pages,
          title: cookbook.name,
          to: `/cookbooks/${cookbook.slug as string}`,
        };
      });
    });

    const createLinks = [
      {
        icon: $globals.icons.link,
        title: i18n.t("general.import"),
        subtitle: i18n.t("new-recipe.import-by-url"),
        to: "/recipe/create/url",
        restricted: true,
      },
      { divider: true },
      {
        icon: $globals.icons.edit,
        title: i18n.t("general.create"),
        subtitle: i18n.t("new-recipe.create-manually"),
        to: "/recipe/create/new",
        restricted: true,
      },
      { divider: true },
      {
        icon: $globals.icons.pages,
        title: i18n.t("sidebar.cookbook"),
        subtitle: i18n.t("sidebar.create-cookbook"),
        to: "/group/cookbooks",
        restricted: true,
      },
    ];

    const bottomLink = [
      {
        icon: $globals.icons.cog,
        title: i18n.t("general.settings"),
        to: "/admin/site-settings",
        restricted: true,
      },
    ];

    const topLinks = [
      {
        icon: $globals.icons.calendarMultiselect,
        title: i18n.t("meal-plan.meal-planner"),
        to: "/group/mealplan/planner",
        restricted: true,
      },
      {
        icon: $globals.icons.formatListCheck,
        title: i18n.t("shopping-list.shopping-lists"),
        to: "/shopping-lists",
        restricted: true,
      },
      {
        icon: $globals.icons.viewModule,
        to: "/recipes/all",
        title: i18n.t("sidebar.all-recipes"),
      },
      {
        icon: $globals.icons.search,
        to: "/search",
        title: i18n.t("sidebar.search"),
      },
      {
        icon: $globals.icons.tags,
        to: "/recipes/categories",
        title: i18n.t("sidebar.categories"),
      },
      {
        icon: $globals.icons.tags,
        to: "/recipes/tags",
        title: i18n.t("sidebar.tags"),
      },
      {
        icon: $globals.icons.potSteam,
        to: "/recipes/tools",
        title: i18n.t("tool.tools"),
      },
    ];

    return { cookbookLinks, createLinks, bottomLink, topLinks, isAdmin, languageDialog, toggleDark, sidebar };
  },
});
</script>
