<template>
  <v-container>
    <BasePageTitle>
      <template #header>
        <v-img max-height="175" max-width="175" :src="require('~/static/svgs/manage-recipes.svg')"></v-img>
      </template>
      <template #title> {{ $t('data-pages.data-management') }} </template>
      {{ $t('data-pages.data-management-description') }}
      <template #content>
        <div>
          <BaseOverflowButton
            :btn-text="buttonText"
            mode="link"
            rounded
            :items="DATA_TYPE_OPTIONS"
          >
          </BaseOverflowButton>
        </div>
      </template>
    </BasePageTitle>
    <section>
      <v-scroll-x-transition>
        <NuxtChild />
      </v-scroll-x-transition>
    </section>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, useContext, useRoute } from "@nuxtjs/composition-api";

export default defineComponent({
  middleware: ["auth", "can-organize-only"],
  props: {
    value: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const { i18n } = useContext();
    const buttonLookup: { [key: string]: string } = {
      recipes: i18n.tc("general.recipes"),
      recipeActions: i18n.tc("recipe.recipe-actions"),
      foods: i18n.tc("general.foods"),
      units: i18n.tc("general.units"),
      labels: i18n.tc("data-pages.labels.labels"),
      categories: i18n.tc("category.categories"),
      tags: i18n.tc("tag.tags"),
      tools: i18n.tc("tool.tools"),
    };

    const route = useRoute();

    const DATA_TYPE_OPTIONS = computed(() => [
      {
        text: i18n.tc("general.recipes"),
        value: "new",
        to: "/group/data/recipes",
      },
      {
        text: i18n.tc("recipe.recipe-actions"),
        value: "new",
        to: "/group/data/recipe-actions",
        divider: true,
      },
      {
        text: i18n.tc("general.foods"),
        value: "url",
        to: "/group/data/foods",
      },
      {
        text: i18n.tc("general.units"),
        value: "new",
        to: "/group/data/units",
      },
      {
        text: i18n.tc("data-pages.labels.labels"),
        value: "new",
        to: "/group/data/labels",
        divider: true,
      },
      {
        text: i18n.tc("category.categories"),
        value: "new",
        to: "/group/data/categories",
      },
      {
        text: i18n.tc("tag.tags"),
        value: "new",
        to: "/group/data/tags",
      },
      {
        text: i18n.tc("tool.tools"),
        value: "new",
        to: "/group/data/tools",
      }
    ]);

    const buttonText = computed(() => {
      const last = route.value.path
        .split("/")
        .pop()
        // convert hypenated-values to camelCase
        ?.replace(/-([a-z])/g, function (g) {
          return g[1].toUpperCase();
        })

      if (last) {
        return buttonLookup[last];
      }

      return i18n.tc("data-pages.select-data");
    });

    return {
      buttonText,
      DATA_TYPE_OPTIONS
    };
  },
  head() {
    return {
      title: this.$tc("data-pages.data-management"),
    };
  },
});
</script>
