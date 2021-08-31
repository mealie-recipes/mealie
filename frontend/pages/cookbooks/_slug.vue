<template>
  <v-container v-if="book" fluid>
    <BaseCardSectionTitle :title="book.name"> </BaseCardSectionTitle>
    <v-tabs v-model="tab" show-arrows>
      <v-tab v-for="(cat, index) in book.categories" :key="index">
        {{ cat.name }}
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab" >
      <v-tab-item v-for="(cat, idx) in book.categories" :key="`tabs` + idx">
        <RecipeCardSection class="mb-5 mx-1" :recipes="cat.recipes" />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script lang="ts">
import RecipeCardSection from "@/components/Domain/Recipe/RecipeCardSection.vue";
import { defineComponent, useRoute, ref } from "@nuxtjs/composition-api";
import { useCookbook } from "~/composables/use-cookbooks";
export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const route = useRoute();
    const slug = route.value.params.slug;
    const { getOne } = useCookbook();

    const tab = ref(null);

    const book = getOne(slug);

    return {
      book,
      tab,
    };
  },
});
</script>

<style scoped>
</style>