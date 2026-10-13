<template>
  <v-navigation-drawer
    v-model="modelValue"
    :width="240"
    floating
    class="d-print-none position-fixed mealie-sidebar"
    touchless
  >
    <AnnouncementDialog v-model="showAnnouncementsDialog" />
    <LanguageDialog v-model="state.languageDialog" />

    <div class="mealie-sidebar__inner">
      <!-- Brand -->
      <div class="mealie-sidebar__brand">
        <RouterLink :to="homeLink" class="mealie-sidebar__brand-link">
          <span class="mealie-brand-mark">M</span>
          <span class="mealie-sidebar__brand-name">Mealie</span>
        </RouterLink>
        <button
          type="button"
          class="mealie-sidebar__icon-btn mealie-hit-target"
          :aria-label="$t('search.search')"
          :title="`${$t('search.search')} (${shortcutLabel})`"
          @click="globalSearch.openDialog()"
        >
          <v-icon size="18">
            {{ $globals.icons.search }}
          </v-icon>
        </button>
      </div>

      <slot />

      <!-- Primary Links -->
      <nav v-if="topLink" class="mealie-sidebar__nav">
        <template v-for="nav in topLink" :key="nav.key || nav.title">
          <template v-if="!nav.restricted || isOwnGroup">
            <!-- Multi Items -->
            <template v-if="nav.children">
              <button
                type="button"
                class="mealie-sidebar__item"
                :aria-expanded="!!state.dropDowns[nav.title]"
                @click="state.dropDowns[nav.title] = !state.dropDowns[nav.title]"
              >
                <span class="mealie-sidebar__item-label">
                  <v-icon size="18" class="mealie-sidebar__icon">{{ nav.icon }}</v-icon>
                  {{ nav.title }}
                </span>
                <v-icon size="16" class="mealie-sidebar__chevron" :class="{ 'mealie-sidebar__chevron--open': state.dropDowns[nav.title] }">
                  {{ $globals.icons.chevronRight }}
                </v-icon>
              </button>
              <div v-show="state.dropDowns[nav.title]" class="mealie-sidebar__children">
                <template v-for="child in nav.children" :key="child.key || child.title">
                  <RouterLink
                    v-if="!child.restricted || isOwnGroup"
                    :to="child.to || ''"
                    class="mealie-sidebar__item"
                    :class="{ 'mealie-sidebar__item--active': isActive(child) }"
                  >
                    <span class="mealie-sidebar__item-label">
                      <v-icon size="18" class="mealie-sidebar__icon">{{ child.icon }}</v-icon>
                      {{ child.title }}
                    </span>
                  </RouterLink>
                </template>
              </div>
            </template>

            <!-- Single Item -->
            <RouterLink
              v-else
              :to="nav.to || ''"
              class="mealie-sidebar__item"
              :class="{ 'mealie-sidebar__item--active': isActive(nav) }"
            >
              <span class="mealie-sidebar__item-label">
                <v-icon size="18" class="mealie-sidebar__icon">{{ nav.icon }}</v-icon>
                {{ nav.title }}
              </span>
              <span v-if="nav.count !== undefined" class="mealie-sidebar__count">{{ nav.count }}</span>
            </RouterLink>
          </template>
        </template>
      </nav>

      <!-- Secondary Links -->
      <template v-if="secondaryLinks && secondaryLinks.length > 0">
        <div class="mealie-sidebar__section">
          {{ secondaryHeader }}
        </div>
        <nav class="mealie-sidebar__nav">
          <template v-for="nav in secondaryLinks" :key="nav.key || nav.title">
            <template v-if="!nav.restricted || isOwnGroup">
              <!-- Multi Items, e.g. another household's cookbooks -->
              <template v-if="nav.children">
                <button
                  type="button"
                  class="mealie-sidebar__item mealie-sidebar__item--compact"
                  :aria-expanded="!!state.dropDowns[nav.title]"
                  @click="state.dropDowns[nav.title] = !state.dropDowns[nav.title]"
                >
                  <span class="mealie-sidebar__item-label">
                    <v-icon size="16" class="mealie-sidebar__icon">{{ nav.icon }}</v-icon>
                    {{ nav.title }}
                  </span>
                  <v-icon size="16" class="mealie-sidebar__chevron" :class="{ 'mealie-sidebar__chevron--open': state.dropDowns[nav.title] }">
                    {{ $globals.icons.chevronRight }}
                  </v-icon>
                </button>
                <div v-show="state.dropDowns[nav.title]" class="mealie-sidebar__children">
                  <RouterLink
                    v-for="child in nav.children"
                    :key="child.key || child.title"
                    :to="child.to || ''"
                    class="mealie-sidebar__item mealie-sidebar__item--compact"
                    :class="{ 'mealie-sidebar__item--active': isActive(child) }"
                  >
                    <span class="mealie-sidebar__item-label">
                      <span v-if="child.color" class="mealie-sidebar__swatch" :style="{ background: child.color }" />
                      <v-icon v-else size="16" class="mealie-sidebar__icon">{{ child.icon }}</v-icon>
                      <span class="mealie-sidebar__truncate">{{ child.title }}</span>
                    </span>
                    <span v-if="child.count !== undefined" class="mealie-sidebar__count">{{ child.count }}</span>
                  </RouterLink>
                </div>
              </template>

              <!-- Single Item -->
              <RouterLink
                v-else
                :to="nav.to || ''"
                class="mealie-sidebar__item mealie-sidebar__item--compact"
                :class="{ 'mealie-sidebar__item--active': isActive(nav) }"
              >
                <span class="mealie-sidebar__item-label">
                  <span v-if="nav.color" class="mealie-sidebar__swatch" :style="{ background: nav.color }" />
                  <v-icon v-else size="16" class="mealie-sidebar__icon">{{ nav.icon }}</v-icon>
                  <span class="mealie-sidebar__truncate">{{ nav.title }}</span>
                </span>
                <span v-if="nav.count !== undefined" class="mealie-sidebar__count">{{ nav.count }}</span>
              </RouterLink>
            </template>
          </template>
        </nav>
      </template>

      <div class="mealie-sidebar__spacer" />

      <!-- Bottom Navigation Links -->
      <nav class="mealie-sidebar__nav">
        <button
          v-if="loggedIn && announcementsEnabled"
          type="button"
          class="mealie-sidebar__item mealie-sidebar__item--compact"
          @click="showAnnouncementsDialog = !showAnnouncementsDialog"
        >
          <span class="mealie-sidebar__item-label">
            <v-icon size="16" class="mealie-sidebar__icon">{{ $globals.icons.bullhornVariant }}</v-icon>
            {{ $t('announcements.announcements') }}
          </span>
          <span v-if="newAnnouncements.length" class="mealie-sidebar__badge">{{ newAnnouncements.length }}</span>
        </button>
        <v-menu location="end bottom" :offset="15">
          <template #activator="{ props: menuProps }">
            <button
              type="button"
              class="mealie-sidebar__item mealie-sidebar__item--compact"
              v-bind="menuProps"
            >
              <span class="mealie-sidebar__item-label">
                <v-icon size="16" class="mealie-sidebar__icon">{{ $globals.icons.cog }}</v-icon>
                {{ $t('general.settings') }}
              </span>
            </button>
          </template>
          <v-list density="comfortable" color="primary">
            <v-list-item :prepend-icon="$globals.icons.translate" :title="$t('sidebar.language')" @click="state.languageDialog=true" />
            <v-list-item :prepend-icon="$vuetify.theme.current.dark ? $globals.icons.weatherSunny : $globals.icons.weatherNight" :title="$vuetify.theme.current.dark ? $t('settings.theme.light-mode') : $t('settings.theme.dark-mode')" @click="toggleDark" />
            <v-divider v-if="loggedIn" class="my-2" />
            <v-list-item v-if="loggedIn" :prepend-icon="$globals.icons.cog" :title="$t('profile.user-settings')" to="/user/profile" />
            <v-list-item v-if="canManage" :prepend-icon="$globals.icons.manageData" :title="$t('data-pages.data-management')" to="/group/data" />
            <v-divider v-if="isAdmin" class="my-2" />
            <v-list-item v-if="isAdmin" :prepend-icon="$globals.icons.wrench" :title="$t('settings.admin-settings')" to="/admin/site-settings" />
            <v-divider v-if="loggedIn" class="my-2" />
            <v-list-item v-if="loggedIn" :prepend-icon="$globals.icons.logout" :title="$t('user.logout')" @click="logout" />
          </v-list>
        </v-menu>
      </nav>

      <!-- User Profile -->
      <div class="mealie-sidebar__user">
        <template v-if="loggedIn && sessionUser">
          <RouterLink :to="userProfileLink || ''" class="mealie-sidebar__user-link">
            <span class="mealie-sidebar__avatar">
              {{ initials }}
              <img
                v-if="!avatarFailed"
                :src="avatarUrl"
                alt=""
                @error="avatarFailed = true"
              >
            </span>
            <span class="mealie-sidebar__user-text">
              <span class="mealie-sidebar__user-name">{{ sessionUser.fullName }}</span>
              <span v-if="sessionUser.household" class="mealie-sidebar__user-household">{{ sessionUser.household }}</span>
            </span>
          </RouterLink>
          <RouterLink
            v-if="isOwnGroup && userFavoritesLink"
            :to="userFavoritesLink"
            class="mealie-sidebar__icon-btn mealie-hit-target"
            :aria-label="$t('user.favorite-recipes')"
            :title="$t('user.favorite-recipes')"
          >
            <v-icon size="16">
              {{ $globals.icons.heart }}
            </v-icon>
          </RouterLink>
        </template>
        <RouterLink v-else to="/login" class="mealie-sidebar__item mealie-sidebar__item--compact w-100">
          <span class="mealie-sidebar__item-label">
            <v-icon size="16" class="mealie-sidebar__icon">{{ $globals.icons.user }}</v-icon>
            {{ $t("user.login") }}
          </span>
        </RouterLink>
      </div>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import type { SideBarLink, SidebarLinks } from "~/types/application-types";
import AnnouncementDialog from "~/components/Domain/Announcement/AnnouncementDialog.vue";
import { useToggleDarkMode } from "~/composables/use-utils";
import { useAnnouncements } from "~/composables/use-announcements";
import { searchShortcutLabel, useGlobalSearch } from "~/composables/use-global-search";

const props = defineProps({
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
  secondaryHeader: {
    type: String,
    default: "",
  },
});

const modelValue = defineModel<boolean>({ default: false });

const auth = useMealieAuth();
const route = useRoute();
const sessionUser = computed(() => auth.user.value);
const { loggedIn, isOwnGroup } = useLoggedInState();
const isAdmin = computed(() => auth.user.value?.admin);
const canManage = computed(() => auth.user.value?.canManage);

const homeLink = computed(() => {
  const slug = (route.params.groupSlug as string) || auth.user.value?.groupSlug;
  return slug ? `/g/${slug}` : "/";
});
const userFavoritesLink = computed(() => auth.user.value ? `/user/${auth.user.value.id}/favorites` : undefined);
const userProfileLink = computed(() => auth.user.value ? "/user/profile" : undefined);

const initials = computed(() => {
  const name = sessionUser.value?.fullName || sessionUser.value?.username || "";
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(part => part[0]!.toUpperCase())
    .join("");
});
const avatarFailed = ref(false);
const avatarUrl = computed(() => {
  const user = sessionUser.value;
  return user ? `/api/media/users/${user.id}/profile.webp?cacheKey=${user.cacheKey ?? ""}` : "";
});
watch(avatarUrl, () => {
  avatarFailed.value = false;
});

const toggleDark = useToggleDarkMode();
const globalSearch = useGlobalSearch();
const shortcutLabel = searchShortcutLabel();

const showAnnouncementsDialog = ref(false);
const { announcementsEnabled, newAnnouncements } = useAnnouncements();

const state = reactive({
  dropDowns: {} as Record<string, boolean>,
  languageDialog: false as boolean,
});

const allLinks = computed(() => [...props.topLink, ...(props.secondaryLinks || [])]);

function flatten(links: SideBarLink[]): SideBarLink[] {
  return links.flatMap(link => [link, ...flatten(link.children || [])]);
}

/**
 * Only the most specific matching link is highlighted, so a recipe page lights up "Recipes"
 * while the recipe finder, which lives under the same path, lights up only itself.
 */
const activeLink = computed(() => {
  const path = route.path.replace(/\/$/, "");
  let best: SideBarLink | null = null;
  for (const link of flatten(allLinks.value)) {
    const to = link.to?.replace(/\/$/, "");
    if (!to || !(path === to || path.startsWith(to + "/"))) {
      continue;
    }
    if (!best || to.length > (best.to?.length ?? 0)) {
      best = link;
    }
  }
  return best;
});

function isActive(link: SideBarLink) {
  return activeLink.value === link;
}

function initDropdowns() {
  allLinks.value.forEach((link) => {
    const containsActive = !!link.children?.some(child => child === activeLink.value);
    state.dropDowns[link.title] = state.dropDowns[link.title] || link.childrenStartExpanded || containsActive;
  });
}
watch(allLinks, initDropdowns, { deep: true, immediate: true });

async function logout() {
  try {
    await auth.signOut("/login?direct=1");
  }
  catch (e) {
    console.error(e);
  }
}
</script>

<style scoped>
.mealie-sidebar {
  background: var(--mealie-sidebar) !important;
  border-right: 1px solid var(--mealie-hairline) !important;
  color: var(--mealie-ink-secondary);
}

.mealie-sidebar__inner {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-height: 100%;
  padding: 22px 14px 10px;
  box-sizing: border-box;
}

.mealie-sidebar__brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px 20px 10px;
}

.mealie-sidebar__brand-link {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--mealie-ink);
  text-decoration: none;
}

.mealie-sidebar__brand-name {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.mealie-sidebar__icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--mealie-text-tertiary);
  cursor: pointer;
  flex-shrink: 0;
}

.mealie-sidebar__icon-btn:hover {
  background: var(--mealie-fill-subtle);
  color: var(--mealie-ink);
}

.mealie-sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mealie-sidebar__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  height: 34px;
  padding: 0 10px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--mealie-ink-secondary);
  font: inherit;
  font-size: 14px;
  font-weight: 500;
  text-align: left;
  text-decoration: none;
  white-space: nowrap;
  cursor: pointer;
  box-sizing: border-box;
}

.mealie-sidebar__item:hover {
  background: var(--mealie-fill-subtle);
}

.mealie-sidebar__item:focus-visible,
.mealie-sidebar__icon-btn:focus-visible,
.mealie-sidebar__user-link:focus-visible {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: -2px;
}

.mealie-sidebar__item--compact {
  height: 32px;
  font-weight: 400;
}

/* stacked rows can't borrow space from their neighbours, so on touch screens they grow to 44px */
@media (pointer: coarse) {
  .mealie-sidebar__item,
  .mealie-sidebar__item--compact {
    height: 44px;
  }
}

.mealie-sidebar__item--active,
.mealie-sidebar__item--active:hover {
  background: rgba(var(--v-theme-primary), 0.12);
  color: rgb(var(--v-theme-primary));
  font-weight: 600;
}

.mealie-sidebar__item-label {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.mealie-sidebar__truncate {
  overflow: hidden;
  text-overflow: ellipsis;
}

.mealie-sidebar__icon {
  color: var(--mealie-icon);
  opacity: 1;
}

.mealie-sidebar__item--active .mealie-sidebar__icon {
  color: rgb(var(--v-theme-primary));
}

.mealie-sidebar__chevron {
  color: var(--mealie-text-tertiary);
  transition: transform 0.15s ease;
}

.mealie-sidebar__chevron--open {
  transform: rotate(90deg);
}

.mealie-sidebar__children {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-left: 12px;
}

.mealie-sidebar__section {
  padding: 22px 10px 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--mealie-text-tertiary);
}

.mealie-sidebar__swatch {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

.mealie-sidebar__count {
  font-size: 12px;
  font-weight: 400;
  color: var(--mealie-text-tertiary);
}

.mealie-sidebar__badge {
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: rgb(var(--v-theme-primary));
  color: rgb(var(--v-theme-on-primary));
  font-size: 11px;
  font-weight: 600;
  line-height: 18px;
  text-align: center;
}

.mealie-sidebar__spacer {
  flex: 1;
  min-height: 16px;
}

.mealie-sidebar__user {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  padding-top: 10px;
  border-top: 1px solid var(--mealie-hairline);
}

.mealie-sidebar__user-link {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
  padding: 6px 10px;
  border-radius: 8px;
  color: var(--mealie-ink);
  text-decoration: none;
}

.mealie-sidebar__user-link:hover {
  background: var(--mealie-fill-subtle);
}

.mealie-sidebar__avatar {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 14px;
  background: var(--mealie-avatar);
  color: var(--mealie-avatar-ink);
  font-size: 11px;
  font-weight: 600;
}

.mealie-sidebar__avatar img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mealie-sidebar__user-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.mealie-sidebar__user-name {
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mealie-sidebar__user-household {
  font-size: 12px;
  color: var(--mealie-text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
