<template>
  <div class="mealie-page">
    <header class="mealie-page__header">
      <div class="mealie-page__titles">
        <div v-if="groupName" class="mealie-eyebrow">
          {{ groupName }}
        </div>
        <h1 class="mealie-page__title">
          {{ $t("recipe.timeline") }}
        </h1>
      </div>
    </header>
    <div class="mealie-page__body timeline-page">
      <RecipeTimeline
        v-if="queryFilter"
        v-model="ready"
        show-recipe-cards
        :query-filter="queryFilter"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import RecipeTimeline from "~/components/Domain/Recipe/RecipeTimeline.vue";

definePageMeta({
  middleware: ["auth", "group-only"],
});

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
</script>

<style scoped>
/* the timeline's own filter row sits right under the page header */
.timeline-page :deep(> div > .v-row:first-child) {
  margin: -64px 0 8px !important;
}
</style>
