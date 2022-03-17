<template>
  <v-container>
    <BasePageTitle>
      <template #header>
        <v-img max-height="175" max-width="175" :src="require('~/static/svgs/manage-recipes.svg')"></v-img>
      </template>
      <template #title> Data Management </template>
      Select which data set you want to make changes to.
      <BannerExperimental class="mt-5"></BannerExperimental>
      <template #content>
        <div>
          <BaseOverflowButton
            :btn-text="buttonText"
            mode="link"
            rounded
            :items="[
              {
                text: 'Foods',
                value: 'url',
                to: '/group/data/foods',
              },
              {
                text: 'Units',
                value: 'new',
                to: '/group/data/units',
              },
              // {
              //   text: 'Labels',
              //   value: 'new',
              //   to: '/group/data/labels',
              // },
            ]"
          >
          </BaseOverflowButton>
        </div>
      </template>
    </BasePageTitle>
    <section>
      <NuxtChild />
    </section>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, useRoute } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    value: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const buttonLookup: { [key: string]: string } = {
      foods: "Foods",
      units: "Units",
      labels: "Labels",
    };

    const route = useRoute();

    const buttonText = computed(() => {
      const last = route.value.path.split("/").pop();

      if (last) {
        return buttonLookup[last];
      }

      return "Select Data";
    });

    return {
      buttonText,
    };
  },
  head: {
    title: "Data Management",
  },
});
</script>
