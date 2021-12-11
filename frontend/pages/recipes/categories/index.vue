<template>
  <v-container>
    <RecipeCategoryTagToolPage v-if="categories" :items="categories" item-type="categories" />
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
    const categories = useAsync(async () => {
      const { data } = await userApi.categories.getAll();

      if (data) {
        return data;
      }
    });

    return {
      categories,
    };
  },
  // head: {
  //   // @ts-ignore
  //   title: this.$t("sidebar.categories") as string,
  // },
});
</script>