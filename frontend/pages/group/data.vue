<template>
  <v-container>
    <BasePageTitle>
      <template #header>
        <v-img
          width="100%"
          max-height="175"
          max-width="175"
          :src="require('~/static/svgs/manage-recipes.svg')"
        />
      </template>
      <template #title>
        {{ $t('data-pages.data-management') }}
      </template>
      {{ $t('data-pages.data-management-description') }}
      <template #content>
        <div>
          <BaseOverflowButton
            :btn-text="buttonText"
            mode="link"
            rounded
            :items="DATA_TYPE_OPTIONS"
          />
        </div>
      </template>
    </BasePageTitle>
    <section>
      <v-scroll-x-transition>
        <div>
          <NuxtPage />
        </div>
      </v-scroll-x-transition>
    </section>
  </v-container>
</template>

<script lang="ts">
export default defineNuxtComponent({
  middleware: ["sidebase-auth", "can-organize-only"],
  setup() {
    const i18n = useI18n();
    const buttonLookup: { [key: string]: string } = {
      recipes: i18n.t("general.recipes"),
      recipeActions: i18n.t("recipe.recipe-actions"),
      foods: i18n.t("general.foods"),
      units: i18n.t("general.units"),
      labels: i18n.t("data-pages.labels.labels"),
      categories: i18n.t("category.categories"),
      tags: i18n.t("tag.tags"),
      tools: i18n.t("tool.tools"),
    };

    const route = useRoute();

    const DATA_TYPE_OPTIONS = computed(() => [
      {
        text: i18n.t("general.recipes"),
        value: "new",
        to: "/group/data/recipes",
      },
      {
        text: i18n.t("recipe.recipe-actions"),
        value: "new",
        to: "/group/data/recipe-actions",
        divider: true,
      },
      {
        text: i18n.t("general.foods"),
        value: "url",
        to: "/group/data/foods",
      },
      {
        text: i18n.t("general.units"),
        value: "new",
        to: "/group/data/units",
      },
      {
        text: i18n.t("data-pages.labels.labels"),
        value: "new",
        to: "/group/data/labels",
        divider: true,
      },
      {
        text: i18n.t("category.categories"),
        value: "new",
        to: "/group/data/categories",
      },
      {
        text: i18n.t("tag.tags"),
        value: "new",
        to: "/group/data/tags",
      },
      {
        text: i18n.t("tool.tools"),
        value: "new",
        to: "/group/data/tools",
      },
    ]);

    const buttonText = computed(() => {
      const last = route.path
        .split("/")
        .pop()
      // convert hypenated-values to camelCase
        ?.replace(/-([a-z])/g, function (g) {
          return g[1].toUpperCase();
        });

      if (last) {
        return buttonLookup[last];
      }

      return i18n.t("data-pages.select-data");
    });

    useSeoMeta({
      title: i18n.t("data-pages.data-management"),
    });

    return {
      buttonText,
      DATA_TYPE_OPTIONS,
    };
  },
});
</script>
