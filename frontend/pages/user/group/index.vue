<template>
  <v-container class="narrow-container">
    {{ group }}
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-group-settings.svg')"></v-img>
      </template>
      <template #title> Group Settings </template>
      These items are shared within your group. Editing one of them will change it for the whole group!
    </BasePageTitle>
    <v-card tag="section" outlined>
      <v-card-text>
        <BaseCardSectionTitle title="Mealplan Categories">
          Set the categories below for the ones that you want to be included in your mealplan random generation.
          <div class="mt-2">
            <BaseButton save @click="actions.updateAll()" />
          </div>
        </BaseCardSectionTitle>
        <DomainRecipeCategoryTagSelector v-if="categories" v-model="categories" />
      </v-card-text>
    </v-card>
    <section>
      <BaseCardSectionTitle class="mt-10" title="Preferences"> </BaseCardSectionTitle>
      <v-checkbox class="mt-n4" label="Show advanced features (API Keys, Webhooks, and Data Management)"></v-checkbox>
    </section>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { useGroup } from "~/composables/use-groups";

export default defineComponent({
  setup() {
    const { categories, actions } = useGroup();

    return {
      categories,
      actions,
    };
  },
});
</script>
    
