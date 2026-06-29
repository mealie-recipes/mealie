<template>
  <div>
    <v-form ref="domForm" @submit.prevent="createRecipe">
      <div>
        <v-card-title class="headline">
          {{ $t("recipe.create-recipe-from-plaintext") }}
        </v-card-title>
        <v-card-text>
          <p>{{ $t("recipe.create-recipe-from-plaintext-description") }}</p>
          <v-container class="px-0">
            <v-textarea
              v-model="recipeText"
              :label="$t('recipe.recipe-text')"
              :disabled="state.loading"
              rows="12"
              auto-grow
              outlined
              clearable
            />
            <v-checkbox
              v-model="shouldTranslate"
              color="primary"
              hide-details
              :label="$t('recipe.should-translate-description')"
              :disabled="state.loading"
            />
          </v-container>
        </v-card-text>
        <v-card-actions>
          <div class="w-100 d-flex flex-column align-center">
            <p style="width: 250px">
              <BaseButton
                rounded
                block
                type="submit"
                :loading="state.loading"
                :disabled="!recipeText"
              />
            </p>
            <p v-if="state.loading" class="mb-0">
              {{ $t("recipe.please-wait-text-processing") }}
            </p>
          </div>
        </v-card-actions>
      </div>
    </v-form>
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { useNewRecipeOptions } from "~/composables/use-new-recipe-options";
import type { VForm } from "~/types/auto-forms";

const state = reactive({
  loading: false,
});

const i18n = useI18n();
const api = useUserApi();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug || "");

const domForm = ref<VForm | null>(null);
const recipeText = ref("");
const shouldTranslate = ref(true);

const { navigateToRecipe } = useNewRecipeOptions();

async function createRecipe() {
  if (!recipeText.value) {
    return;
  }

  state.loading = true;

  const translateLanguage = shouldTranslate.value ? i18n.locale : undefined;
  const { data, error } = await api.recipes.createOneFromText(recipeText.value, translateLanguage?.value);
  if (error || !data) {
    alert.error(i18n.t("events.something-went-wrong"));
    state.loading = false;
  }
  else {
    navigateToRecipe(data, groupSlug.value, `/g/${groupSlug.value}/r/create/plaintext`);
  }
}
</script>
