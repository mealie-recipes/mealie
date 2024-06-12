<template>
  <div>
    <v-form ref="domUrlForm" @submit.prevent="debugUrl(recipeUrl)">
      <div>
        <v-card-title class="headline"> {{ $t('recipe.recipe-debugger') }} </v-card-title>
        <v-card-text>
          {{ $t('recipe.recipe-debugger-description') }}
          <v-text-field
            v-model="recipeUrl"
            :label="$t('new-recipe.recipe-url')"
            validate-on-blur
            :prepend-inner-icon="$globals.icons.link"
            autofocus
            filled
            clearable
            rounded
            class="rounded-lg mt-2"
            :rules="[validators.url]"
            :hint="$t('new-recipe.url-form-hint')"
            persistent-hint
          />
        </v-card-text>
        <v-card-text v-if="appInfo && appInfo.enableOpenai">
          {{ $t('recipe.recipe-debugger-use-openai-description') }}
          <v-checkbox v-model="useOpenAI" :label="$t('recipe.use-openai')"></v-checkbox>
        </v-card-text>
        <v-card-actions class="justify-center">
          <div style="width: 250px">
            <BaseButton :disabled="recipeUrl === null" rounded block type="submit" color="info" :loading="loading">
              <template #icon>
                {{ $globals.icons.robot }}
              </template>
              {{ $t('recipe.debug') }}
            </BaseButton>
          </div>
        </v-card-actions>
      </div>
    </v-form>
    <section v-if="debugData">
      <v-checkbox v-model="debugTreeView" :label="$t('recipe.tree-view')"></v-checkbox>
      <LazyRecipeJsonEditor
        v-model="debugData"
        class="primary"
        :options="{
          mode: debugTreeView ? 'tree' : 'code',
          search: false,
          indentation: 4,
          mainMenuBar: false,
        }"
        height="700px"
      />
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, ref, useRouter, computed, useRoute } from "@nuxtjs/composition-api";
import { useAppInfo, useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { Recipe } from "~/lib/api/types/recipe";

export default defineComponent({
  setup() {
    const state = reactive({
      error: false,
      loading: false,
      useOpenAI: false,
    });

    const api = useUserApi();
    const route = useRoute();
    const router = useRouter();
    const appInfo = useAppInfo();

    const recipeUrl = computed({
      set(recipe_import_url: string | null) {
        if (recipe_import_url !== null) {
          recipe_import_url = recipe_import_url.trim();
          router.replace({ query: { ...route.value.query, recipe_import_url } });
        }
      },
      get() {
        return route.value.query.recipe_import_url as string | null;
      },
    });

    const debugTreeView = ref(false);

    const debugData = ref<Recipe | null>(null);

    async function debugUrl(url: string | null) {
      if (url === null) {
        return;
      }

      state.loading = true;

      const { data } = await api.recipes.testCreateOneUrl(url, state.useOpenAI);

      state.loading = false;
      debugData.value = data;
    }

    return {
      appInfo,
      recipeUrl,
      debugTreeView,
      debugUrl,
      debugData,
      ...toRefs(state),
      validators,
    };
  },
});
</script>
