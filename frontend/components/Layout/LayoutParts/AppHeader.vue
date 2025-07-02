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
      <v-btn
        v-if="loggedIn"
        :variant="smAndUp ? 'text' : undefined"
        :icon="xs"
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

export default defineNuxtComponent({
  components: { RecipeDialogSearch },
  props: {
    menu: {
      type: Boolean,
      default: true,
    },
  },
  setup() {
    const $auth = useMealieAuth();
    const { loggedIn } = useLoggedInState();
    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");
    const { xs, smAndUp } = useDisplay();

    const routerLink = computed(() => groupSlug.value ? `/g/${groupSlug.value}` : "/");
    const domSearchDialog = ref<InstanceType<typeof RecipeDialogSearch> | null>(null);

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
        await $auth.signOut({ callbackUrl: "/login?direct=1" });
      }
      catch (e) {
        console.error(e);
      }
    }

    return {
      activateSearch,
      domSearchDialog,
      routerLink,
      loggedIn,
      logout,
      xs, smAndUp,
    };
  },
});
</script>

<style scoped>
.v-toolbar {
  z-index: 1010 !important;
}
</style>
