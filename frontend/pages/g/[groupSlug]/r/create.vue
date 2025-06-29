<template>
  <div>
    <v-container class="flex-column">
      <BasePageTitle divider>
        <template #header>
          <v-img
            width="100%"
            max-height="175"
            max-width="175"
            :src="require('~/static/svgs/recipes-create.svg')"
          />
        </template>
        <template #title>
          {{ $t('recipe.recipe-creation') }}
        </template>
        <template #content>
          <div class="flex-1-1 d-flex flex-column justify-center align-center ga-2">
            <p>{{ $t('recipe.select-one-of-the-various-ways-to-create-a-recipe') }}</p>
            <div class="ml-auto">
              <BaseOverflowButton
                v-model="subpage"
                rounded
                :items="subpages"
              />
            </div>
          </div>
        </template>
      </BasePageTitle>
      <section>
        <NuxtPage />
      </section>
    </v-container>

    <AdvancedOnly>
      <v-container class="d-flex justify-center align-center my-4">
        <router-link
          :to="`/group/migrations`"
          class="text-primary"
        > {{ $t('recipe.looking-for-migrations') }}</router-link>
      </v-container>
    </AdvancedOnly>
  </div>
</template>

<script lang="ts">
import { useAppInfo } from "~/composables/api";
import type { MenuItem } from "~/components/global/BaseOverflowButton.vue";
import AdvancedOnly from "~/components/global/AdvancedOnly.vue";

export default defineNuxtComponent({
  components: { AdvancedOnly },
  middleware: ["sidebase-auth", "group-only"],
  setup() {
    const i18n = useI18n();
    const $auth = useMealieAuth();
    const $globals = useNuxtApp().$globals;

    useSeoMeta({
      title: i18n.t("general.create"),
    });

    const appInfo = useAppInfo();
    const enableOpenAIImages = computed(() => appInfo.value?.enableOpenaiImageServices);

    const subpages = computed<MenuItem[]>(() => [
      {
        icon: $globals.icons.link,
        text: i18n.t("recipe.import-with-url"),
        value: "url",
      },
      {
        icon: $globals.icons.link,
        text: i18n.t("recipe.bulk-url-import"),
        value: "bulk",
      },
      {
        icon: $globals.icons.codeTags,
        text: i18n.t("recipe.import-from-html-or-json"),
        value: "html",
      },
      {
        icon: $globals.icons.fileImage,
        text: i18n.t("recipe.create-from-images"),
        value: "image",
        hide: !enableOpenAIImages.value,
      },
      {
        icon: $globals.icons.edit,
        text: i18n.t("recipe.create-recipe"),
        value: "new",
      },
      {
        icon: $globals.icons.zip,
        text: i18n.t("recipe.import-with-zip"),
        value: "zip",
      },
      {
        icon: $globals.icons.robot,
        text: i18n.t("recipe.debug-scraper"),
        value: "debug",
      },
    ]);

    const route = useRoute();
    const router = useRouter();
    const groupSlug = computed(() => route.params.groupSlug || $auth.user.value?.groupSlug || "");

    const subpage = computed({
      set(subpage: string) {
        router.push({ path: `/g/${groupSlug.value}/r/create/${subpage}`, query: route.query });
      },
      get() {
        return route.path.split("/").pop() ?? "url";
      },
    });

    return {
      groupSlug,
      subpages,
      subpage,
    };
  },
});
</script>
