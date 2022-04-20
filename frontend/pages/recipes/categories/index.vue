<template>
  <v-container>
    <RecipeCategoryTagToolPage v-if="categories" :items="categories" item-type="categories" @delete="removeCat" />
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useAsync } from "@nuxtjs/composition-api";
import RecipeCategoryTagToolPage from "~/components/Domain/Recipe/RecipeCategoryTagToolPage.vue";
import { useUserApi } from "~/composables/api";
import { useAsyncKey } from "~/composables/use-utils";

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
    }, useAsyncKey());

    function removeCat(id: string) {
      if (categories.value) {
        for (let i = 0; i < categories.value.length; i++) {
          if (categories.value[i].id === id) {
            categories.value.splice(i, 1);
            break;
          }
        }
      }
    }

    return {
      categories,
      removeCat,
    };
  },
});
</script>
