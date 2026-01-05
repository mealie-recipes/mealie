<template>
  <v-app-bar
    clipped-left
    density="compact"
    app
    color="primary"
    dark
    class="d-print-none"
  >
    <slot />
    <router-link :to="routerLink">
      <v-btn
        icon
        color="white"
      >
        <v-icon size="40"> {{ $globals.icons.primary }} </v-icon>
      </v-btn>
    </router-link>

    <div
      btn
      class="pl-2"
    >
      <v-toolbar-title
        style="cursor: pointer"
        @click="$router.push(routerLink)"
      >
        Mealie
      </v-toolbar-title>
    </div>
    <RecipeDialogSearch ref="domSearchDialog" />

    <v-spacer />

    <!-- Navigation Menu -->
    <template v-if="menu">
      <v-responsive
        v-if="!xs"
        max-width="250"
        @click="activateSearch"
      >
        <v-text-field
          readonly
          class="mt-1"
          rounded
          variant="solo-filled"
          density="compact"
          flat
          :prepend-inner-icon="$globals.icons.search"
          bg-color="primary-darken-1"
          :placeholder="$t('search.search-hint')"
        />
      </v-responsive>
      <v-btn
        v-else
        icon
        @click="activateSearch"
      >
        <v-icon> {{ $globals.icons.search }}</v-icon>
      </v-btn>
      <div v-if="loggedIn && sessionUser" class="mx-1">
        <LanguageDialog v-model="languageDialog" />
        <v-menu z-index="2020">
          <template #activator="{ props }">
            <v-btn v-bind="props" icon data-testid="user-menu-button">
              <UserAvatar list :user-id="sessionUser.id" :tooltip="false" />
            </v-btn>
          </template>
          <v-list density="comfortable" color="primary" data-testid="user-menu">
            <v-list-item :title="sessionUser.fullName ?? undefined" :to="userProfileLink">
              <template #prepend>
                <!-- TODO: horizontally center avatar with other icons in menu (why isn't it automatically centered?) -->
                <UserAvatar list :user-id="sessionUser.id" :tooltip="false" />
              </template>
            </v-list-item>
            <v-divider class="my-2" />
            <v-list-item :prepend-icon="$globals.icons.translate" :title="$t('sidebar.language')" @click="languageDialog=true" />
            <!-- TODO: prevent menu from closing when toggling light/dark mode -->
            <v-list-item :prepend-icon="$vuetify.theme.current.dark ? $globals.icons.weatherSunny : $globals.icons.weatherNight" :title="$vuetify.theme.current.dark ? $t('settings.theme.light-mode') : $t('settings.theme.dark-mode')" @click="toggleDark" />
            <!-- TODO: what was the use case for sidebar settings in logged-out state? -->
            <v-divider v-if="loggedIn" class="my-2" />
            <v-list-item v-if="canManage" :prepend-icon="$globals.icons.manageData" :title="$t('data-pages.data-management')" to="/group/data" />
            <v-divider v-if="isAdmin" class="my-2" />
            <v-list-item v-if="isAdmin" :prepend-icon="$globals.icons.wrench" :title="$t('settings.admin-settings')" to="/admin/site-settings" />
            <v-divider class="my-2" />
            <v-list-item v-if="loggedIn" :prepend-icon="$globals.icons.logout" :title="$t('user.logout')" @click="logout()" />
          </v-list>
        </v-menu>
      </div>
      <v-btn
        v-else
        variant="text"
        nuxt
        to="/login"
      >
        <v-icon start>
          {{ $globals.icons.user }}
        </v-icon>
        {{ $t("user.login") }}
      </v-btn>
    </template>
  </v-app-bar>
</template>

<script lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import RecipeDialogSearch from "~/components/Domain/Recipe/RecipeDialogSearch.vue";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";

export default defineNuxtComponent({
  components: {
    RecipeDialogSearch,
    UserAvatar,
  },
  props: {
    menu: {
      type: Boolean,
      default: true,
    },
  },
  setup() {
    const $auth = useMealieAuth();
    const { loggedIn } = useLoggedInState();
    const isAdmin = computed(() => $auth.user.value?.admin);
    const canManage = computed(() => $auth.user.value?.canManage);
    const userProfileLink = computed(() => $auth.user.value ? "/user/profile" : undefined);
    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");
    const { xs, smAndUp } = useDisplay();

    const routerLink = computed(() => groupSlug.value ? `/g/${groupSlug.value}` : "/");
    const domSearchDialog = ref<InstanceType<typeof RecipeDialogSearch> | null>(null);

    const toggleDark = useToggleDarkMode();

    const state = reactive({
      languageDialog: false,
    });

    function activateSearch() {
      domSearchDialog.value?.open();
    }

    function handleKeyEvent(e: KeyboardEvent) {
      const activeTag = document.activeElement?.tagName;
      if (e.key === "/" && activeTag !== "INPUT" && activeTag !== "TEXTAREA") {
        e.preventDefault();
        activateSearch();
      }
    }

    onMounted(() => {
      document.addEventListener("keydown", handleKeyEvent);
    });

    onBeforeUnmount(() => {
      document.removeEventListener("keydown", handleKeyEvent);
    });

    async function logout() {
      try {
        await $auth.signOut("/login?direct=1");
      }
      catch (e) {
        console.error(e);
      }
    }

    return {
      ...toRefs(state),
      activateSearch,
      canManage,
      domSearchDialog,
      isAdmin,
      loggedIn,
      logout,
      routerLink,
      sessionUser: $auth.user,
      smAndUp,
      toggleDark,
      userProfileLink,
      xs,
    };
  },
});
</script>

<style scoped lang="scss">
.v-toolbar {
  z-index: 2010 !important;
}
</style>
