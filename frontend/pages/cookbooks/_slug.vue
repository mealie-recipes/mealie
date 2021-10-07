<template>
  <v-container v-if="book" fluid>
    <v-app-bar color="transparent" flat class="mt-n1 rounded">
      <v-icon large left> {{ $globals.icons.pages }} </v-icon>
      <v-toolbar-title class="headline"> {{ book.name }} </v-toolbar-title>
    </v-app-bar>
    <v-card flat>
      <v-card-text class="py-0">
        {{ book.description }}
      </v-card-text>
    </v-card>
    <v-tabs v-model="tab" show-arrows>
      <v-tab v-for="(cat, index) in book.categories" :key="index">
        {{ cat.name }}
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item v-for="(cat, idx) in book.categories" :key="`tabs` + idx">
        <RecipeCardSection class="mb-5 mx-1" :recipes="cat.recipes" />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useRoute, ref, useMeta } from "@nuxtjs/composition-api";
import RecipeCardSection from "@/components/Domain/Recipe/RecipeCardSection.vue";
import { useCookbook } from "~/composables/use-group-cookbooks";
export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const route = useRoute();
    const slug = route.value.params.slug;
    const { getOne } = useCookbook();

    const tab = ref(null);

    const book = getOne(slug);

    useMeta(() => {
      return {
        title: book?.value?.name || "Cookbook",
      };
    });

    return {
      book,
      tab,
    };
  },
  head: {}, // Must include for useMeta
});
</script>

<style scoped>
</style>