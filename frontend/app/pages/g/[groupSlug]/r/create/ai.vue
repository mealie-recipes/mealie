<template>
  <v-form ref="domUrlForm" @submit.prevent="createRecipe">
    <div>
      <v-card-title class="headline">
        {{ $t('recipe.import-with-ai') }}
      </v-card-title>
      <v-card-text v-if="!aiEnabled">
        <v-alert type="info" variant="tonal">
          {{ $t('recipe.import-with-ai-provider-required') }}
        </v-alert>
      </v-card-text>
      <v-card-text v-else>
        <p>{{ $t('recipe.import-with-ai-description') }}</p>
        <p v-if="videosEnabled">
          {{ $t('recipe.import-with-ai-video-description') }}
        </p>
        <br>
        <p>
          {{ $t('recipe.import-with-ai-without-ai-question') }}
          <router-link :to="urlImporterTarget" class="text-primary">{{ $t('recipe.import-with-ai-use-url-import') }}</router-link>.
        </p>
        <p>
          {{ $t('recipe.scrape-recipe-have-raw-html-or-json-data') }}
          <router-link :to="htmlOrJsonImporterTarget" class="text-primary">{{ $t('recipe.scrape-recipe-you-can-import-from-raw-data-directly') }}</router-link>.
        </p>

        <v-text-field
          v-model="recipeUrl"
          :label="$t('new-recipe.recipe-url')"
          :prepend-inner-icon="$globals.icons.link"
          validate-on="blur"
          variant="solo-filled"
          clearable
          rounded
          :rules="[validators.urlOptional]"
          :hint="$t('recipe.import-with-ai-url-hint')"
          persistent-hint
          class="mt-8 mb-4"
          :disabled="state.loading"
        />

        <v-switch
          v-model="state.isEditJSON"
          :label="$t('recipe.json-editor')"
          color="primary"
          class="mt-2"
          :disabled="state.loading"
          @change="handleIsEditJson"
        />
        <RecipeJsonEditor
          v-if="state.isEditJSON"
          v-model="newRecipeData"
          height="250px"
          mode="code"
          :main-menu-bar="false"
        />
        <v-textarea
          v-else
          v-model="newRecipeData"
          :label="$t('recipe.import-with-ai-content')"
          :prepend-inner-icon="$globals.icons.textBox"
          validate-on="blur"
          variant="solo-filled"
          clearable
          rounded
          :hint="$t('recipe.import-with-ai-content-hint')"
          persistent-hint
          :disabled="state.loading"
        />

        <div v-if="imagesEnabled" class="mt-6">
          <RecipeImportImages v-model="uploadedImages" :disabled="state.loading" />
        </div>
        <v-alert
          v-else
          type="info"
          variant="tonal"
          class="mt-6"
        >
          {{ $t('recipe.import-with-ai-image-provider-required') }}
        </v-alert>

        <v-checkbox
          v-model="translateRecipe"
          color="primary"
          hide-details
          :label="$t('recipe.should-translate-description')"
          :disabled="state.loading"
        />
        <div class="d-flex align-center">
          <v-checkbox
            v-model="createNewOrganizers"
            color="primary"
            hide-details
            :label="$t('recipe.create-new-organizers')"
            :disabled="state.loading"
          />
          <v-tooltip location="bottom" max-width="300">
            <template #activator="{ props: tooltipProps }">
              <v-icon v-bind="tooltipProps" size="small" class="ms-2">
                {{ $globals.icons.help }}
              </v-icon>
            </template>
            <span>{{ $t('recipe.create-new-organizers-hint') }}</span>
          </v-tooltip>
        </div>
        <v-checkbox
          v-model="stayInEditMode"
          color="primary"
          hide-details
          :label="$t('recipe.stay-in-edit-mode')"
          :disabled="state.loading"
        />
        <v-checkbox
          v-model="parseRecipe"
          color="primary"
          hide-details
          :label="$t('recipe.parse-recipe-ingredients-after-import')"
          :disabled="state.loading"
        />
      </v-card-text>
      <v-card-actions v-if="aiEnabled" class="justify-center">
        <div style="width: 100%" class="text-center">
          <div style="width: 250px; margin: 0 auto">
            <BaseButton
              :disabled="!hasSource"
              rounded
              block
              type="submit"
              :loading="state.loading"
            />
          </div>
          <v-card-text class="py-2">
            <!-- render &nbsp; to maintain layout -->
            {{ createStatus }}&nbsp;
          </v-card-text>
        </div>
      </v-card-actions>

      <v-expand-transition>
        <v-alert
          v-if="state.error"
          color="error"
          class="mt-6 white--text"
        >
          <v-card-title class="ma-0 pa-0">
            <v-icon
              start
              color="white"
              size="x-large"
            >
              {{ $globals.icons.robot }}
            </v-icon>
            {{ $t("new-recipe.error-title") }}
          </v-card-title>
          <v-divider class="my-3 mx-2" />

          <div class="force-url-white">
            <p>{{ state.errorMessage || $t("recipe.import-with-ai-error-details") }}</p>
          </div>
        </v-alert>
      </v-expand-transition>
    </div>
  </v-form>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { useGroupSelf } from "~/composables/use-groups";
import { useTagStore } from "~/composables/store/use-tag-store";
import { useNewRecipeOptions } from "~/composables/use-new-recipe-options";
import { validators } from "~/composables/use-validators";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  key: route => route.path,
});

const state = reactive({
  error: false,
  errorMessage: "",
  loading: false,
  isEditJSON: false,
});

const i18n = useI18n();
const api = useUserApi();
const auth = useMealieAuth();
const route = useRoute();
const tags = useTagStore();
const { group } = useGroupSelf();

const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const urlImporterTarget = computed(() => `/g/${groupSlug.value}/r/create/url`);
const htmlOrJsonImporterTarget = computed(() => `/g/${groupSlug.value}/r/create/html`);
const aiEnabled = computed(() => !!group.value?.aiProviderSettings?.aiEnabled);
const imagesEnabled = computed(() => !!group.value?.aiProviderSettings?.imageProviderEnabled);
const videosEnabled = computed(() => !!group.value?.aiProviderSettings?.audioProviderEnabled);

const domUrlForm = ref<VForm | null>(null);
const recipeUrl = ref<string | null>(null);
const newRecipeData = ref<string | object | null>(null);
const uploadedImages = ref<(Blob | File)[]>([]);
const createStatus = ref<string | null>(null);

const {
  stayInEditMode,
  parseRecipe,
  translateRecipe,
  createNewOrganizers,
  navigateToRecipe,
} = useNewRecipeOptions({
  enableImportKeywords: false,
  enableImportCategories: false,
  enableTranslateRecipe: true,
  enableCreateNewOrganizers: true,
});

const contentAsString = computed(() => {
  const data = newRecipeData.value;
  if (!data) {
    return null;
  }

  return typeof data === "string" ? data : JSON.stringify(data);
});

const hasSource = computed(() => !!(recipeUrl.value || contentAsString.value || uploadedImages.value.length));

function handleIsEditJson() {
  if (state.isEditJSON) {
    if (newRecipeData.value) {
      try {
        newRecipeData.value = JSON.parse(newRecipeData.value as string);
      }
      catch {
        newRecipeData.value = { data: newRecipeData.value };
      }
    }
    else {
      newRecipeData.value = {};
    }
  }
  else if (newRecipeData.value && Object.keys(newRecipeData.value).length > 0) {
    newRecipeData.value = JSON.stringify(newRecipeData.value);
  }
  else {
    newRecipeData.value = null;
  }
}
handleIsEditJson();

async function createRecipe() {
  if (!hasSource.value) {
    return;
  }

  const isValid = await domUrlForm.value?.validate();
  if (!isValid?.valid) {
    return;
  }

  state.error = false;
  state.errorMessage = "";
  state.loading = true;

  const { data, error } = await api.recipes.createOneWithAI(
    {
      content: contentAsString.value,
      url: recipeUrl.value,
      images: uploadedImages.value,
      translateLanguage: translateRecipe.value ? i18n.locale.value : null,
      createNewOrganizers: createNewOrganizers.value,
    },
    (message: string) => createStatus.value = message,
  );

  createStatus.value = null;

  if (error || !data) {
    state.error = true;
    state.errorMessage = error?.message || "";
    state.loading = false;
    return;
  }

  if (createNewOrganizers.value) {
    tags.actions.refresh();
  }

  navigateToRecipe(data, groupSlug.value, `/g/${groupSlug.value}/r/create/ai`);
}
</script>

<style scoped>
.force-url-white a {
  color: white !important;
}
</style>
