<template>
  <v-app-bar clipped-left dense app color="primary" dark class="d-print-none">
    <slot />
    <router-link to="/">
      <v-btn icon>
        <v-icon size="40"> {{ $globals.icons.primary }} </v-icon>
      </v-btn>
    </router-link>

    <div btn class="pl-2">
      <v-toolbar-title style="cursor: pointer" @click="$router.push('/')"> Mealie </v-toolbar-title>
    </div>
    <RecipeDialogSearch ref="domSearchDialog" />

    <v-spacer></v-spacer>

    <!-- Navigation Menu -->
    <template v-if="menu">
      <div v-if="!$vuetify.breakpoint.xs" style="max-width: 500px" @click="activateSearch">
        <v-text-field
          readonly
          class="mt-6 rounded-xl"
          rounded
          dark
          solo
          dense
          flat
          :prepend-inner-icon="$globals.icons.search"
          background-color="primary lighten-1"
          color="white"
          placeholder="Press '/'"
        >
        </v-text-field>
      </div>
      <v-btn v-else icon @click="activateSearch">
        <v-icon> {{ $globals.icons.search }}</v-icon>
      </v-btn>
      <v-btn v-if="$auth.loggedIn" text @click="$auth.logout()">
        <v-icon left>{{ $globals.icons.logout }}</v-icon>
        {{ $t("user.logout") }}
      </v-btn>
      <v-btn v-else text nuxt to="/login">
        <v-icon left>{{ $globals.icons.user }}</v-icon>
        {{ $t("user.login") }}
      </v-btn>
    </template>
  </v-app-bar>
</template>

<script lang="ts">
import { defineComponent, onBeforeUnmount, onMounted, ref } from "@nuxtjs/composition-api";
import RecipeDialogSearch from "~/components/Domain/Recipe/RecipeDialogSearch.vue";

export default defineComponent({
  components: { RecipeDialogSearch },
  props: {
    menu: {
      type: Boolean,
      default: true,
    },
  },
  setup() {
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

    return {
      activateSearch,
      domSearchDialog,
    };
  },
});
</script>
