<template>
  <v-bottom-navigation grow>
    <template v-for="nav in topLinks" :key="nav.key || nav.title">
      <v-btn
        :to="nav.to"
        :icon="nav.icon"
        size="3rem"
        variant="plain"
      />
    </template>
  </v-bottom-navigation>
</template>

<script lang="ts">
export default defineNuxtComponent({
  setup() {
    const { $globals } = useNuxtApp();
    const $auth = useMealieAuth();

    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");

    const topLinks = computed<any[]>(() => [
      {
        icon: $globals.icons.calendarMultiselect,
        to: "/household/mealplan/planner/view",
      },
      {
        icon: $globals.icons.silverwareForkKnife,
        to: `/g/${groupSlug.value}`,
      },
      {
        icon: $globals.icons.formatListCheck,
        to: "/shopping-lists",
      },
    ]);

    return {
      topLinks,
    };
  },
});
</script>
