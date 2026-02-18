<template>
  <div>
    <v-card-title class="headline">
      {{ $t("recipe.import-with-ai") }}
    </v-card-title>
    <v-card-text>
      <p>{{ $t("recipe.import-with-ai-description") }}</p>
    </v-card-text>

    <v-tabs v-model="activeTab" color="primary">
      <v-tab value="url">
        {{ $t("recipe.ai-tab-url") }}
      </v-tab>
      <v-tab value="text">
        {{ $t("recipe.ai-tab-text") }}
      </v-tab>
      <v-tab
        v-if="$appInfo.enableOpenaiImageServices"
        value="photo"
      >
        {{ $t("recipe.ai-tab-photo") }}
      </v-tab>
    </v-tabs>

    <v-tabs-window v-model="activeTab">
      <!-- URL Tab -->
      <v-tabs-window-item value="url">
        <v-form
          ref="domUrlForm"
          class="mt-4"
          @submit.prevent="createByUrl"
        >
          <v-text-field
            v-model="recipeUrl"
            :label="$t('new-recipe.recipe-url')"
            :prepend-inner-icon="$globals.icons.link"
            validate-on="blur"
            autofocus
            variant="solo-filled"
            clearable
            class="rounded-lg mt-2"
            rounded
            :rules="[validators.url]"
            :hint="$t('new-recipe.url-form-hint')"
            persistent-hint
          />
          <v-checkbox
            v-model="importKeywordsAsTags"
            color="primary"
            hide-details
            :label="$t('recipe.import-original-keywords-as-tags')"
          />
          <v-checkbox
            v-model="importCategories"
            color="primary"
            hide-details
            :label="$t('recipe.import-original-categories')"
          />
          <v-checkbox
            v-model="stayInEditMode"
            color="primary"
            hide-details
            :label="$t('recipe.stay-in-edit-mode')"
          />
          <v-checkbox
            v-model="parseRecipe"
            color="primary"
            hide-details
            :label="$t('recipe.parse-recipe-ingredients-after-import')"
          />
          <v-card-actions class="justify-center">
            <div style="width: 250px">
              <BaseButton
                :disabled="recipeUrl === null || recipeUrl === ''"
                rounded
                block
                type="submit"
                :loading="urlLoading"
              />
            </div>
          </v-card-actions>
        </v-form>
        <v-expand-transition>
          <v-alert
            v-if="urlError"
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
            <p>{{ $t("new-recipe.error-details") }}</p>
          </v-alert>
        </v-expand-transition>
      </v-tabs-window-item>

      <!-- Text Tab -->
      <v-tabs-window-item value="text">
        <v-form
          ref="domTextForm"
          class="mt-4"
          @submit.prevent="createByText"
        >
          <p class="mb-3">
            {{ $t("recipe.ai-text-description") }}
          </p>
          <v-textarea
            v-model="recipeText"
            :placeholder="$t('recipe.ai-text-placeholder')"
            rows="10"
            variant="solo-filled"
            class="rounded-lg"
            rounded
          />
          <v-checkbox
            v-model="stayInEditMode"
            color="primary"
            hide-details
            :label="$t('recipe.stay-in-edit-mode')"
          />
          <v-checkbox
            v-model="parseRecipe"
            color="primary"
            hide-details
            :label="$t('recipe.parse-recipe-ingredients-after-import')"
          />
          <v-card-actions class="justify-center">
            <div style="width: 250px">
              <BaseButton
                :disabled="!recipeText || recipeText.trim() === ''"
                rounded
                block
                type="submit"
                :loading="textLoading"
              />
            </div>
          </v-card-actions>
          <p v-if="textLoading" class="text-center mb-0">
            {{ $t("recipe.ai-please-wait-text-processing") }}
          </p>
        </v-form>
        <v-expand-transition>
          <v-alert
            v-if="textError"
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
            <p>{{ $t("new-recipe.error-details") }}</p>
          </v-alert>
        </v-expand-transition>
      </v-tabs-window-item>

      <!-- Photo Tab -->
      <v-tabs-window-item
        v-if="$appInfo.enableOpenaiImageServices"
        value="photo"
      >
        <v-form
          ref="domPhotoForm"
          class="mt-4"
          @submit.prevent="createFromPhotos"
        >
          <p>{{ $t("recipe.create-recipe-from-an-image-description") }}</p>
          <v-container class="px-0">
            <AppButtonUpload
              class="ml-auto"
              url="none"
              file-name="images"
              accept="image/*"
              :text="uploadedImages.length ? $t('recipe.upload-more-images') : $t('recipe.upload-images')"
              :text-btn="false"
              :post="false"
              :multiple="true"
              @uploaded="uploadImages"
            />
            <div v-if="uploadedImages.length" class="mt-3">
              <p class="my-2">
                {{ $t("recipe.crop-and-rotate-the-image") }}
              </p>
              <v-row>
                <v-col
                  v-for="(imageUrl, index) in uploadedImagesPreviewUrls"
                  :key="index"
                  cols="12"
                  sm="6"
                  lg="4"
                  xl="3"
                >
                  <v-col>
                    <ImageCropper
                      :img="imageUrl"
                      cropper-height="100%"
                      cropper-width="100%"
                      :submitted="photoLoading"
                      class="mt-4 mb-2"
                      @save="(croppedImage) => updateUploadedImage(index, croppedImage)"
                      @delete="clearImage(index)"
                    />

                    <v-btn
                      v-if="uploadedImages.length > 1"
                      :disabled="photoLoading || index === 0"
                      color="primary"
                      @click="() => setCoverImage(index)"
                    >
                      <v-icon start>
                        {{ index === 0 ? $globals.icons.check : $globals.icons.fileImage }}
                      </v-icon>

                      {{ index === 0 ? $t("recipe.cover-image") : $t("recipe.set-as-cover-image") }}
                    </v-btn>
                  </v-col>
                </v-col>
              </v-row>
            </div>
          </v-container>
          <v-checkbox
            v-if="uploadedImages.length"
            v-model="shouldTranslate"
            color="primary"
            hide-details
            :label="$t('recipe.should-translate-description')"
            :disabled="photoLoading"
          />
          <v-checkbox
            v-if="uploadedImages.length"
            v-model="parseRecipe"
            color="primary"
            hide-details
            :label="$t('recipe.parse-recipe-ingredients-after-import')"
            :disabled="photoLoading"
          />
          <v-card-actions v-if="uploadedImages.length">
            <div class="w-100 d-flex flex-column align-center">
              <p style="width: 250px">
                <BaseButton rounded block type="submit" :loading="photoLoading" />
              </p>
              <p v-if="photoLoading" class="mb-0">
                {{
                  uploadedImages.length > 1
                    ? $t("recipe.please-wait-images-processing")
                    : $t("recipe.please-wait-image-procesing")
                }}
              </p>
            </div>
          </v-card-actions>
        </v-form>
      </v-tabs-window-item>
    </v-tabs-window>
  </div>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import { useTagStore } from "~/composables/store/use-tag-store";
import { useNewRecipeOptions } from "~/composables/use-new-recipe-options";
import { alert } from "~/composables/use-toast";
import { validators } from "~/composables/use-validators";
import type { VForm } from "~/types/auto-forms";

export default defineNuxtComponent({
  setup() {
    definePageMeta({
      key: route => route.path,
    });

    const i18n = useI18n();
    const auth = useMealieAuth();
    const api = useUserApi();
    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
    const tags = useTagStore();

    const {
      importKeywordsAsTags,
      importCategories,
      stayInEditMode,
      parseRecipe,
      navigateToRecipe,
    } = useNewRecipeOptions();

    const activeTab = ref("url");

    // URL tab state
    const recipeUrl = ref<string | null>(null);
    const urlLoading = ref(false);
    const urlError = ref(false);
    const domUrlForm = ref<VForm | null>(null);

    // Text tab state
    const recipeText = ref("");
    const textLoading = ref(false);
    const textError = ref(false);
    const domTextForm = ref<VForm | null>(null);

    // Photo tab state
    const photoLoading = ref(false);
    const domPhotoForm = ref<VForm | null>(null);
    const uploadedImages = ref<(Blob | File)[]>([]);
    const uploadedImageNames = ref<string[]>([]);
    const uploadedImagesPreviewUrls = ref<string[]>([]);
    const shouldTranslate = ref(true);

    const createPagePath = computed(() => `/g/${groupSlug.value}/r/create/openai`);

    // URL tab methods
    async function createByUrl() {
      if (recipeUrl.value === null || recipeUrl.value === "") {
        return;
      }

      if (!domUrlForm.value?.validate()) {
        return;
      }

      urlLoading.value = true;
      urlError.value = false;
      const { response } = await api.recipes.createOneByUrl(
        recipeUrl.value,
        importKeywordsAsTags.value,
        importCategories.value,
        true,
      );

      if (response?.status !== 201) {
        urlError.value = true;
        urlLoading.value = false;
        return;
      }

      if (importKeywordsAsTags.value) {
        tags.actions.refresh();
      }

      navigateToRecipe(response.data, groupSlug.value, createPagePath.value);
    }

    // Text tab methods
    async function createByText() {
      if (!recipeText.value || recipeText.value.trim() === "") {
        return;
      }

      textLoading.value = true;
      textError.value = false;
      const { data, error } = await api.recipes.createOneFromText(recipeText.value);

      if (error || !data) {
        textError.value = true;
        textLoading.value = false;
        return;
      }

      navigateToRecipe(data, groupSlug.value, createPagePath.value);
    }

    // Photo tab methods
    function uploadImages(files: File[]) {
      uploadedImages.value = [...uploadedImages.value, ...files];
      uploadedImageNames.value = [...uploadedImageNames.value, ...files.map(file => file.name)];
      uploadedImagesPreviewUrls.value = [
        ...uploadedImagesPreviewUrls.value,
        ...files.map(file => URL.createObjectURL(file)),
      ];
    }

    function clearImage(index: number) {
      URL.revokeObjectURL(uploadedImagesPreviewUrls.value[index]);
      uploadedImages.value.splice(index, 1);
      uploadedImageNames.value.splice(index, 1);
      uploadedImagesPreviewUrls.value.splice(index, 1);
    }

    function updateUploadedImage(index: number, croppedImage: Blob) {
      uploadedImages.value[index] = croppedImage;
      uploadedImagesPreviewUrls.value[index] = URL.createObjectURL(croppedImage);
    }

    function swapItem(array: any[], i: number, j: number) {
      if (i < 0 || j < 0 || i >= array.length || j >= array.length) {
        return;
      }
      const temp = array[i];
      array[i] = array[j];
      array[j] = temp;
    }

    function setCoverImage(index: number) {
      if (index < 0 || index >= uploadedImages.value.length || index === 0) {
        return;
      }
      swapItem(uploadedImages.value, 0, index);
      swapItem(uploadedImageNames.value, 0, index);
      swapItem(uploadedImagesPreviewUrls.value, 0, index);
    }

    async function createFromPhotos() {
      if (uploadedImages.value.length === 0) {
        return;
      }

      photoLoading.value = true;
      const translateLanguage = shouldTranslate.value ? i18n.locale : undefined;
      const { data, error } = await api.recipes.createOneFromImages(uploadedImages.value, translateLanguage?.value);

      if (error || !data) {
        alert.error(i18n.t("events.something-went-wrong"));
        photoLoading.value = false;
        return;
      }

      navigateToRecipe(data, groupSlug.value, createPagePath.value);
    }

    return {
      activeTab,
      validators,
      // URL tab
      recipeUrl,
      urlLoading,
      urlError,
      domUrlForm,
      importKeywordsAsTags,
      importCategories,
      stayInEditMode,
      parseRecipe,
      createByUrl,
      // Text tab
      recipeText,
      textLoading,
      textError,
      domTextForm,
      createByText,
      // Photo tab
      photoLoading,
      domPhotoForm,
      uploadedImages,
      uploadedImagesPreviewUrls,
      shouldTranslate,
      uploadImages,
      clearImage,
      updateUploadedImage,
      setCoverImage,
      createFromPhotos,
    };
  },
});
</script>
