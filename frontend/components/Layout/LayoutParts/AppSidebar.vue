<template>
  <v-navigation-drawer v-model="showDrawer" class="d-flex flex-column d-print-none position-fixed" touchless>
    <LanguageDialog v-model="languageDialog" />
    <!-- User Profile -->
    <template v-if="loggedIn">
      <v-list-item lines="two" :to="userProfileLink" exact>
        <div class="d-flex align-center ga-2">
          <UserAvatar list :user-id="sessionUser.id" :tooltip="false" />

          <div class="d-flex flex-column justify-start">
            <v-list-item-title class="pr-2 pl-1">
              {{ sessionUser.fullName }}
            </v-list-item-title>
            <v-list-item-subtitle class="opacity-100">
              <v-btn v-if="isOwnGroup" class="px-2 pa-0" variant="text" :to="userFavoritesLink" size="small">
                <v-icon start size="small">
                  {{ $globals.icons.heart }}
                </v-icon>
                {{ $t("user.favorite-recipes") }}
              </v-btn>
            </v-list-item-subtitle>
          </div>
        </div>
      </v-list-item>
      <v-divider />
    </template>

    <slot />

    <!-- Primary Links -->
    <template v-if="topLink">
      <v-list v-model:selected="secondarySelected" nav density="comfortable" color="primary">
        <template v-for="nav in topLink">
          <div v-if="!nav.restricted || isOwnGroup" :key="nav.key || nav.title">
            <!-- Multi Items -->
            <v-list-group
              v-if="nav.children"
              :key="(nav.key || nav.title) + 'multi-item'"
              v-model="dropDowns[nav.title]"
              color="primary"
              :prepend-icon="nav.icon"
              :fluid="true"
            >
              <template #activator="{ props }">
                <v-list-item v-bind="props" :prepend-icon="nav.icon" :title="nav.title" />
              </template>

              <v-list-item
                v-for="child in nav.children"
                :key="child.key || child.title"
                exact
                :to="child.to"
                :prepend-icon="child.icon"
                :title="child.title"
                class="ml-4"
              />
            </v-list-group>

            <!-- Single Item -->
            <template v-else>
              <v-list-item
                :key="(nav.key || nav.title) + 'single-item'"
                exact
                link
                :to="nav.to"
                :prepend-icon="nav.icon"
                :title="nav.title"
              />
            </template>
          </div>
        </template>
      </v-list>
    </template>

    <!-- Secondary Links -->
    <template v-if="secondaryLinks.length > 0">
      <v-divider class="mt-2" />
      <v-list v-model:selected="secondarySelected" nav density="compact" exact>
        <template v-for="nav in secondaryLinks">
          <div v-if="!nav.restricted || isOwnGroup" :key="nav.key || nav.title">
            <!-- Multi Items -->
            <v-list-group
              v-if="nav.children"
              :key="(nav.key || nav.title) + 'multi-item'"
              v-model="dropDowns[nav.title]"
              color="primary"
              :prepend-icon="nav.icon"
              fluid
            >
              <template #activator="{ props }">
                <v-list-item v-bind="props" :prepend-icon="nav.icon" :title="nav.title" />
              </template>

              <v-list-item
                v-for="child in nav.children"
                :key="child.key || child.title"
                exact
                :to="child.to"
                class="ml-2"
                :prepend-icon="child.icon"
                :title="child.title"
              />
            </v-list-group>

            <!-- Single Item -->
            <v-list-item v-else :key="(nav.key || nav.title) + 'single-item'" exact link :to="nav.to">
              <template #prepend>
                <v-icon>{{ nav.icon }}</v-icon>
              </template>
              <v-list-item-title>{{ nav.title }}</v-list-item-title>
            </v-list-item>
          </div>
        </template>
      </v-list>
    </template>

    <!-- Bottom Navigation Links -->
    <template #append>
      <v-list v-model:selected="bottomSelected" nav density="comfortable">
        <v-menu location="end bottom" :offset="15">
          <template #activator="{ props }">
            <v-list-item v-bind="props" :prepend-icon="$globals.icons.cog" :title="$t('general.settings')" />
          </template>
          <v-list density="comfortable" color="primary">
            <v-list-item :prepend-icon="$globals.icons.translate" :title="$t('sidebar.language')" @click="languageDialog=true" />
            <v-list-item :prepend-icon="$vuetify.theme.current.dark ? $globals.icons.weatherSunny : $globals.icons.weatherNight" :title="$vuetify.theme.current.dark ? $t('settings.theme.light-mode') : $t('settings.theme.dark-mode')" @click="toggleDark" />
            <v-divider v-if="loggedIn" class="my-2" />
            <v-list-item v-if="loggedIn" :prepend-icon="$globals.icons.cog" :title="$t('profile.user-settings')" to="/user/profile" />
            <v-list-item v-if="canManage" :prepend-icon="$globals.icons.manageData" :title="$t('data-pages.data-management')" to="/group/data" />
            <v-divider v-if="isAdmin" class="my-2" />
            <v-list-item v-if="isAdmin" :prepend-icon="$globals.icons.wrench" :title="$t('settings.admin-settings')" to="/admin/site-settings" />
          </v-list>
        </v-menu>
      </v-list>
    </template>
  </v-navigation-drawer>
</template>

<script lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import type { SidebarLinks } from "~/types/application-types";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import { useToggleDarkMode } from "~/composables/use-utils";

export default defineNuxtComponent({
  components: {
    UserAvatar,
  },
  props: {
    modelValue: {
      type: Boolean,
      required: false,
      default: false,
    },
    user: {
      type: Object,
      default: null,
    },
    topLink: {
      type: Array as () => SidebarLinks,
      required: true,
    },
    secondaryLinks: {
      type: Array as () => SidebarLinks,
      required: false,
      default: null,
    },
  },
  emits: ["update:modelValue"],
  setup(props, context) {
    const $auth = useMealieAuth();
    const { loggedIn, isOwnGroup } = useLoggedInState();
    const isAdmin = computed(() => $auth.user.value?.admin);
    const canManage = computed(() => $auth.user.value?.canManage);

    const userFavoritesLink = computed(() => $auth.user.value ? `/user/${$auth.user.value.id}/favorites` : undefined);
    const userProfileLink = computed(() => $auth.user.value ? "/user/profile" : undefined);

    const toggleDark = useToggleDarkMode();

    const state = reactive({
      dropDowns: {} as Record<string, boolean>,
      topSelected: null as string[] | null,
      secondarySelected: null as string[] | null,
      bottomSelected: null as string[] | null,
      hasOpenedBefore: false as boolean,
      languageDialog: false as boolean,
    });
    // model to control the drawer
    const showDrawer = computed({
      get: () => props.modelValue,
      set: value => context.emit("update:modelValue", value),
    });

    const allLinks = computed(() => [...props.topLink, ...(props.secondaryLinks || [])]);
    function initDropdowns() {
      allLinks.value.forEach((link) => {
        state.dropDowns[link.title] = link.childrenStartExpanded || false;
      });
    }
    watch(
      () => allLinks,
      () => {
        initDropdowns();
      },
      {
        deep: true,
      },
    );

    return {
      ...toRefs(state),
      userFavoritesLink,
      userProfileLink,
      showDrawer,
      loggedIn,
      isAdmin,
      canManage,
      isOwnGroup,
      sessionUser: $auth.user,
      toggleDark,
    };
  },
});
</script>

<style scoped>
@media print {
  .no-print {
    display: none;
  }
}

.favorites-link {
  text-decoration: none;
}

.favorites-link:hover {
  text-decoration: underline;
}
</style>
