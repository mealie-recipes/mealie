<template>
  <v-app v-if="ready" dark>
    <v-card-title>
      <slot>
        <h1 class="mx-auto">{{ $t("page.404-page-not-found") }}</h1>
      </slot>
    </v-card-title>
    <div class="d-flex justify-space-around">
      <div class="d-flex align-center">
        <p class="primary--text">4</p>
        <v-icon color="primary" class="mx-auto mb-0" size="200">
          {{ $globals.icons.primary }}
        </v-icon>
        <p class="primary--text">4</p>
      </div>
    </div>
    <v-card-actions>
      <v-spacer></v-spacer>
      <slot name="actions">
        <v-btn v-for="(button, index) in buttons" :key="index" nuxt :to="button.to" color="primary">
          <v-icon left> {{ button.icon }} </v-icon>
          {{ button.text }}
        </v-btn>
      </slot>
      <v-spacer></v-spacer>
    </v-card-actions>
  </v-app>
</template>

<script lang="ts">
import { defineComponent, ref, useContext, useMeta, useRoute, useRouter } from "@nuxtjs/composition-api";

export default defineComponent({
  layout: "basic",
  props: {
    error: {
      type: Object,
      default: null,
    },
  },
  setup(props) {
    const { $auth, $globals, i18n } = useContext();
    const ready = ref(false);

    const route = useRoute();
    const router = useRouter();

    async function insertGroupSlugIntoRoute() {
      const groupSlug = ref($auth.user?.groupSlug);
      if (!groupSlug.value) {
        return;
      }

      let replaceRoute = false;
      let routeVal = route.value.fullPath || "/";
      if (routeVal[0] !== "/") {
        routeVal = `/${routeVal}`;
      }

      // replace "recipe" in URL with "r"
      if (routeVal.includes("/recipe/")) {
        replaceRoute = true;
        routeVal = routeVal.replace("/recipe/", "/r/");
      }

      // insert groupSlug into URL
      const routeComponents = routeVal.split("/");
      if (routeComponents.length < 2 || routeComponents[1].toLowerCase() !== "g") {
        replaceRoute = true;
        routeVal = `/g/${groupSlug.value}${routeVal}`;
      }

      if (replaceRoute) {
        await router.replace(routeVal);
      }
    }

    async function handle404() {
      const normalizedRoute = route.value.fullPath.replace(/\/$/, "");
      const newRoute = normalizedRoute.replace(/^\/group\/(mealplan|members|notifiers|webhooks)(\/.*)?$/, "/household/$1$2");

      if (newRoute !== normalizedRoute) {
        await router.replace(newRoute);
      } else {
        await insertGroupSlugIntoRoute();
      }

      ready.value = true;
    }

    if (props.error.statusCode === 404) {
      handle404();
    } else {
      ready.value = true;
    }

    useMeta({
      title:
        props.error.statusCode === 404
          ? (i18n.t("page.404-not-found") as string)
          : (i18n.t("page.an-error-occurred") as string),
    });

    const buttons = [
      { icon: $globals.icons.home, to: "/", text: i18n.t("general.home") },
    ];

    return {
      buttons,
      ready,
    };
  },
  // Needed for useMeta
  head: {},
});
</script>

<style scoped>
h1 {
  font-size: 20px;
}
p {
  padding-bottom: 0 !important;
  margin-bottom: 0 !important;
  font-size: 200px;
}
</style>
