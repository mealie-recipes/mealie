<template>
  <v-container>
    <RecipeCategoryTagToolPage v-if="tools" :items="tools" item-type="tools" />
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useAsync } from "@nuxtjs/composition-api";
import RecipeCategoryTagToolPage from "~/components/Domain/Recipe/RecipeCategoryTagToolPage.vue";
import { useUserApi } from "~/composables/api";

export default defineComponent({
  components: {
    RecipeCategoryTagToolPage,
  },
  setup() {
    const userApi = useUserApi();
    const tools = useAsync(async () => {
      const { data } = await userApi.tools.getAll();

      if (data) {
        return data;
      }
    });
    return {
      tools,
    };
  },
  head: {
    title: "Tools",
  },
});
</script>