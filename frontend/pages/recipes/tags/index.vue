<template>
  <v-container v-if="tags">
    <v-app-bar color="transparent" flat class="mt-n1 rounded">
      <v-icon large left>
        {{ $globals.icons.tags }}
      </v-icon>
      <v-toolbar-title class="headline"> {{ $t("tag.tags") }} </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>
    <section v-for="(items, key, idx) in tagsByLetter" :key="'header' + idx" :class="idx === 1 ? null : 'my-4'">
      <BaseCardSectionTitle :title="key"> </BaseCardSectionTitle>
      <v-row>
        <v-col v-for="(item, index) in items" :key="'cat' + index" cols="12" :sm="12" :md="6" :lg="4" :xl="3">
          <v-card hover :to="`/recipes/tags/${item.slug}`">
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
import { defineComponent, useAsync, computed } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
import { useAsyncKey } from "~/composables/use-utils";

export default defineComponent({
  setup() {
    const api = useApiSingleton();

    const tags = useAsync(async () => {
      const { data } = await api.tags.getAll();
      return data;
    }, useAsyncKey());

    const tagsByLetter: any = computed(() => {
      const tagsByLetter: { [key: string]: Array<any> } = {};

      if (!tags.value) return tagsByLetter;

      tags.value.forEach((item) => {
        const letter = item.name[0].toUpperCase();
        if (!tagsByLetter[letter]) {
          tagsByLetter[letter] = [];
        }

        tagsByLetter[letter].push(item);
      });

      return tagsByLetter;
    });

    return { tags, api, tagsByLetter };
  },
});
</script>
  
<style scoped>
</style>