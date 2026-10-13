<template>
  <v-app-bar
    v-if="!hidden"
    density="compact"
    flat
    app
    class="d-print-none mealie-app-bar"
  >
    <slot />
    <RouterLink :to="routerLink" class="mealie-app-bar__brand">
      <span class="mealie-brand-mark">M</span>
      <span class="mealie-app-bar__title">Mealie</span>
    </RouterLink>

    <v-spacer />

    <!-- Navigation Menu -->
    <template v-if="menu">
      <button
        v-if="!xs"
        type="button"
        class="mealie-app-bar__search mealie-hit-target"
        @click="activateSearch"
      >
        <v-icon size="16">
          {{ $globals.icons.search }}
        </v-icon>
        <span class="mealie-app-bar__search-text">{{ $t("search.search") }}</span>
        <kbd class="mealie-kbd">{{ shortcutLabel }}</kbd>
      </button>
      <v-btn
        v-else
        icon
        :aria-label="$t('search.search')"
        @click="activateSearch"
      >
        <v-icon> {{ $globals.icons.search }}</v-icon>
      </v-btn>
      <v-btn
        v-if="loggedIn"
        :variant="smAndUp ? 'text' : undefined"
        :icon="xs"
        class="mr-1"
        @click="logout()"
      >
        <v-icon :start="smAndUp">
          {{ $globals.icons.logout }}
        </v-icon>
        {{ smAndUp ? $t("user.logout") : "" }}
      </v-btn>
      <v-btn
        v-else
        variant="text"
        nuxt
        to="/login"
        class="mr-1"
      >
        <v-icon start>
          {{ $globals.icons.user }}
        </v-icon>
        {{ $t("user.login") }}
      </v-btn>
    </template>
  </v-app-bar>
  <!-- outside the bar so search keeps working on desktop, where the sidebar replaces the bar -->
  <RecipeDialogSearch v-if="menu" ref="domSearchDialog" />
</template>

<script setup lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { isSearchShortcut, useGlobalSearch, searchShortcutLabel } from "~/composables/use-global-search";
import type RecipeDialogSearch from "~/components/Domain/Recipe/RecipeDialogSearch.vue";

const props = defineProps({
  menu: {
    type: Boolean,
    default: true,
  },
  /** Hide the bar on large screens, where the permanent sidebar carries the brand and navigation */
  hideOnDesktop: {
    type: Boolean,
    default: false,
  },
});
const auth = useMealieAuth();
const { loggedIn } = useLoggedInState();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const { xs, smAndUp, lgAndUp } = useDisplay();

const hidden = computed(() => props.hideOnDesktop && lgAndUp.value);
const routerLink = computed(() => groupSlug.value ? `/g/${groupSlug.value}` : "/");
const domSearchDialog = ref<InstanceType<typeof RecipeDialogSearch> | null>(null);
const shortcutLabel = searchShortcutLabel();

const globalSearch = useGlobalSearch();

function activateSearch() {
  domSearchDialog.value?.open();
}

watch(globalSearch.dialogRequests, activateSearch);

function handleKeyEvent(e: KeyboardEvent) {
  if (props.menu && isSearchShortcut(e)) {
    e.preventDefault();
    globalSearch.open();
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
    await auth.signOut("/login?direct=1");
  }
  catch (e) {
    console.error(e);
  }
}
</script>

<style scoped>
.v-toolbar {
  z-index: 2010 !important;
}

.mealie-app-bar {
  background: color-mix(in srgb, var(--mealie-canvas) 82%, transparent) !important;
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--mealie-hairline-strong);
  color: var(--mealie-ink) !important;
}

.mealie-app-bar__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 6px;
  color: inherit;
  text-decoration: none;
}

.mealie-app-bar__title {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.mealie-app-bar__search {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 240px;
  height: 32px;
  padding: 0 10px 0 12px;
  margin-right: 8px;
  border: 0;
  border-radius: 10px;
  background: var(--mealie-fill);
  color: var(--mealie-text-tertiary);
  font: inherit;
  font-size: 14px;
  cursor: pointer;
}

.mealie-app-bar__search-text {
  flex: 1;
  text-align: left;
}
</style>

<style>
.mealie-brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 8px;
  background: rgb(var(--v-theme-primary));
  color: rgb(var(--v-theme-on-primary));
  font-size: 15px;
  font-weight: 700;
  line-height: 1;
}

.mealie-kbd {
  font-family: inherit;
  font-size: 12px;
  color: var(--mealie-text-tertiary);
  padding: 1px 6px;
  border-radius: 5px;
  box-shadow: inset 0 0 0 1px var(--mealie-hairline-strong);
  white-space: nowrap;
}
</style>
