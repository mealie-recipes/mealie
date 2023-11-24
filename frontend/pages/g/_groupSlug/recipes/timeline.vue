<template>
  <v-sheet :class="$vuetify.breakpoint.smAndDown ? 'pa-0' : 'px-3 py-0'">
    <BasePageTitle v-if="groupName">
      <template #header>
        <v-img max-height="200" max-width="150" :src="require('~/static/svgs/manage-members.svg')" />
      </template>
      <template #title> {{ $t("recipe.group-global-timeline", { groupName }) }} </template>
    </BasePageTitle>
    <RecipeTimeline v-if="queryFilter" v-model="ready" show-recipe-cards :query-filter="queryFilter" />
  </v-sheet>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import RecipeTimeline from "~/components/Domain/Recipe/RecipeTimeline.vue";

export default defineComponent({
  components: { RecipeTimeline },
  setup() {
    const api = useUserApi();
    const ready = ref<boolean>(false);

    const groupName = ref<string>("");
    const queryFilter = ref<string>("");
    async function fetchGroup() {
      const { data } = await api.groups.getCurrentUserGroup();
      if (data) {
        queryFilter.value = `recipe.group_id="${data.id}"`;
        groupName.value = data.name;
      }

      ready.value = true;
    }

    fetchGroup();
    return {
      groupName,
      queryFilter,
      ready,
    };
  },
  head() {
    return {
      title: this.$t("recipe.timeline") as string,
    };
  },
});
</script>
