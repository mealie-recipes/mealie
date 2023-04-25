<template>
  <v-sheet :class="$vuetify.breakpoint.smAndDown ? 'pa-0' : 'px-3 py-0'">
    <BasePageTitle v-if="groupName" divider>
      <template #header>
        <v-img max-height="200" max-width="150" :src="require('~/static/svgs/manage-members.svg')" />
      </template>
      <template #title> {{ $t("recipe.group-global-timeline", { groupName }) }} </template>
    </BasePageTitle>
    <RecipeTimeline v-model="ready" show-recipe-cards :query-filter="queryFilter" />
  </v-sheet>
</template>

<script lang="ts">
import { defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import RecipeTimeline from "~/components/Domain/Recipe/RecipeTimeline.vue";

export default defineComponent({
  components: { RecipeTimeline },
  setup() {
    const { $auth } = useContext();
    const api = useUserApi();
    const ready = ref<boolean>(false);

    // @ts-expect-error - TS doesn't like the $auth global user attribute
    const groupId: string = $auth.user.groupId;
    const queryFilter = `recipe.group_id="${groupId}"`

    const groupName = ref<string>("");
    async function refreshGroupName() {
      const { data } = await api.groups.getCurrentUserGroup();
      if (data) {
        groupName.value = data.name;
      }
    }

    refreshGroupName();
    ready.value = true;

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
