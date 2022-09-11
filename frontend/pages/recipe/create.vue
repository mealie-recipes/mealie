<template>
  <div>
    <v-container class="flex-column">
      <BasePageTitle divider>
        <template #header>
          <v-img max-height="175" max-width="175" :src="require('~/static/svgs/recipes-create.svg')"></v-img>
        </template>
        <template #title> Recipe Creation </template>
        Select one of the various ways to create a recipe
        <template #content>
          <div class="ml-auto">
            <BaseOverflowButton v-model="subpage" rounded :items="subpages"> </BaseOverflowButton>
          </div>
        </template>
      </BasePageTitle>
      <section>
        <NuxtChild />
      </section>
    </v-container>

    <AdvancedOnly>
      <v-container class="d-flex justify-end">
        <v-btn outlined rounded to="/group/migrations"> Looking For Migrations? </v-btn>
      </v-container>
    </AdvancedOnly>
  </div>
</template>

<script lang="ts">
import { defineComponent, useRouter, useContext, computed, useRoute } from "@nuxtjs/composition-api";
import { MenuItem } from "~/components/global/BaseOverflowButton.vue";
import AdvancedOnly from "~/components/global/AdvancedOnly.vue";

export default defineComponent({
  components: { AdvancedOnly },
  setup() {
    const { $globals } = useContext();

    const subpages: MenuItem[] = [
      {
        icon: $globals.icons.link,
        text: "Import with URL",
        value: "url",
      },
      {
        icon: $globals.icons.edit,
        text: "Create Recipe",
        value: "new",
      },
      {
        icon: $globals.icons.zip,
        text: "Import with .zip",
        value: "zip",
      },
      {
        icon: $globals.icons.fileImage,
        text: "Create recipe from an image",
        value: "ocr",
      },
      {
        icon: $globals.icons.link,
        text: "Bulk URL Import",
        value: "bulk",
      },
      {
        icon: $globals.icons.robot,
        text: "Debug Scraper",
        value: "debug",
      },
    ];

    const route = useRoute();
    const router = useRouter();

    const subpage = computed({
      set(subpage: string) {
        router.push({ path: `/recipe/create/${subpage}`, query: route.value.query });
      },
      get() {
        return route.value.path.split("/").pop() ?? "url";
      },
    });

    return {
      subpages,
      subpage,
    };
  },
  head() {
    return {
      title: this.$t("general.create") as string,
    };
  },
});
</script>
