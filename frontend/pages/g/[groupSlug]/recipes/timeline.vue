<template>
  <div>
    <BasePageTitle
      v-if="groupName"
      class="mt-n4 pt-8"
    >
      <template #header>
        <v-img
          width="100%"
          max-height="200"
          max-width="150"
          :src="require('~/static/svgs/manage-members.svg')"
        />
      </template>
      <template #title>
        {{ $t("recipe.group-global-timeline", { groupName }) }}
      </template>
    </BasePageTitle>
    <v-sheet :class="$vuetify.display.smAndDown ? 'pa-0' : 'px-3 py-0'">
      <RecipeTimeline
        v-if="queryFilter"
        v-model="ready"
        show-recipe-cards
        :query-filter="queryFilter"
      />
    </v-sheet>
  </div>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import RecipeTimeline from "~/components/Domain/Recipe/RecipeTimeline.vue";

export default defineNuxtComponent({
  components: { RecipeTimeline },
  middleware: ["sidebase-auth", "group-only"],
  setup() {
    const i18n = useI18n();
    const api = useUserApi();
    const ready = ref<boolean>(false);

    useSeoMeta({
      title: i18n.t("recipe.timeline"),
    });

    const groupName = ref<string>("");
    const queryFilter = ref<string>("");
    async function fetchHousehold() {
      const { data } = await api.households.getCurrentUserHousehold();
      if (data) {
        queryFilter.value = `recipe.group_id="${data.groupId}"`;
        groupName.value = data.group;
      }

      ready.value = true;
    }

    useAsyncData("house-hold", fetchHousehold);

    return {
      groupName,
      queryFilter,
      ready,
    };
  },
});
</script>
