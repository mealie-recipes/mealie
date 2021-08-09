<template>
  <v-container v-if="categories">
    <v-app-bar color="transparent" flat class="mt-n1 rounded">
      <v-icon large left>
        {{ $globals.icons.tags }}
      </v-icon>
      <v-toolbar-title class="headline"> {{ $t("recipe.categories") }} </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-slide-x-transition hide-on-leave>
      <v-row>
        <v-col v-for="item in categories" :key="item.id" cols="12" :sm="12" :md="6" :lg="4" :xl="3">
          <v-card hover :to="`/recipes/categories/${item.slug}`">
            <v-card-actions>
              <v-icon>
                {{ $globals.icons.tags }}
              </v-icon>
              <v-card-title class="py-1">{{ item.name }}</v-card-title>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-slide-x-transition>
  </v-container>
</template>
  
<script lang="ts">
import { defineComponent, useAsync } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
import { useAsyncKey } from "~/composables/use-utils";

export default defineComponent({
  setup() {
    const api = useApiSingleton();

    const categories = useAsync(async () => {
      const { data } = await api.categories.getAll();
      return data;
    }, useAsyncKey());
    return { categories, api };
  },
});
</script>
  
<style scoped>
</style>