<template>
  <v-container>
    <RecipeCategoryTagToolPage v-if="tools" :items="tools" item-type="tools" @delete="removeTool" />
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
    const tools = useAsync(async () => {
      const { data } = await userApi.tools.getAll();

      if (data) {
        return data;
      }
    }, useAsyncKey());

    function removeTool(id: string) {
      if (tools.value) {
        for (let i = 0; i < tools.value.length; i++) {
          if (tools.value[i].id === id) {
            tools.value.splice(i, 1);
            break;
          }
        }
      }
    }

    return {
      tools,
      removeTool,
    };
  },
});
</script>
