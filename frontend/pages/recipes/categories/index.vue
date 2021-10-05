<template>
  <v-container v-if="categories">
    <v-app-bar color="transparent" flat class="mt-n1 rounded">
      <v-icon large left>
        {{ $globals.icons.tags }}
      </v-icon>
      <v-toolbar-title class="headline"> {{ $t("recipe.categories") }} </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>
    <section v-for="(items, key, idx) in categoriesByLetter" :key="'header' + idx" :class="idx === 1 ? null : 'my-4'">
      <BaseCardSectionTitle :title="key"> </BaseCardSectionTitle>
      <v-row>
        <v-col v-for="(item, index) in items" :key="'cat' + index" cols="12" :sm="12" :md="6" :lg="4" :xl="3">
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
    </section>
  </v-container>
</template>
  
<script lang="ts">
import { computed, defineComponent, useAsync } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
import { useAsyncKey } from "~/composables/use-utils";

export default defineComponent({
  setup() {
    const api = useApiSingleton();

    const categories = useAsync(async () => {
      const { data } = await api.categories.getAll();
      return data;
    }, useAsyncKey());

    const categoriesByLetter: any = computed(() => {
      const catsByLetter: { [key: string]: Array<any> } = {};

      if (!categories.value) return catsByLetter;

      categories.value.forEach((item) => {
        const letter = item.name[0].toUpperCase();
        if (!catsByLetter[letter]) {
          catsByLetter[letter] = [];
        }

        catsByLetter[letter].push(item);
      });

      return catsByLetter;
    });

    return { categories, api, categoriesByLetter };
  },
  head() {
    return {
      title: this.$t("sidebar.categories") as string,
    };
  },
});
</script>
  
<style scoped>
</style>