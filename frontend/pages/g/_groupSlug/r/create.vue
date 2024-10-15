<template>
  <div>
    <v-container class="flex-column">
      <BasePageTitle divider>
        <template #header>
          <v-img max-height="175" max-width="175" :src="require('~/static/svgs/recipes-create.svg')"></v-img>
        </template>
        <template #title> {{ $t('recipe.recipe-creation') }} </template>
        {{ $t('recipe.select-one-of-the-various-ways-to-create-a-recipe') }}
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
      <v-container class="d-flex justify-center align-center my-4">
        <router-link :to="`/group/migrations`"> {{ $t('recipe.looking-for-migrations') }}</router-link>
      </v-container>
    </AdvancedOnly>
  </div>
</template>

<script lang="ts">
import { defineComponent, useRouter, useContext, computed, useRoute } from "@nuxtjs/composition-api";
import { useAppInfo } from "~/composables/api";
import { MenuItem } from "~/components/global/BaseOverflowButton.vue";
import AdvancedOnly from "~/components/global/AdvancedOnly.vue";

export default defineComponent({
  components: { AdvancedOnly },
  middleware: ["auth", "group-only"],
  setup() {
    const { $auth, $globals, i18n } = useContext();

    const appInfo = useAppInfo();
    const enableOpenAIImages = computed(() => appInfo.value?.enableOpenaiImageServices);

    const subpages = computed<MenuItem[]>(() => [
      {
        icon: $globals.icons.link,
        text: i18n.tc("recipe.import-with-url"),
        value: "url",
      },
      {
        icon: $globals.icons.link,
        text: i18n.tc("recipe.bulk-url-import"),
        value: "bulk",
      },
      {
        icon: $globals.icons.codeTags,
        text: i18n.tc("recipe.import-from-html-or-json"),
        value: "html",
      },
      {
        icon: $globals.icons.fileImage,
        text: i18n.tc("recipe.create-from-image"),
        value: "image",
        hide: !enableOpenAIImages.value,
      },
      {
        icon: $globals.icons.edit,
        text: i18n.tc("recipe.create-recipe"),
        value: "new",
      },
      {
        icon: $globals.icons.zip,
        text: i18n.tc("recipe.import-with-zip"),
        value: "zip",
      },
      {
        icon: $globals.icons.robot,
        text: i18n.tc("recipe.debug-scraper"),
        value: "debug",
      },
    ]);

    const route = useRoute();
    const router = useRouter();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

    const subpage = computed({
      set(subpage: string) {
        router.push({ path: `/g/${groupSlug.value}/r/create/${subpage}`, query: route.value.query });
      },
      get() {
        return route.value.path.split("/").pop() ?? "url";
      },
    });

    return {
      groupSlug,
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
