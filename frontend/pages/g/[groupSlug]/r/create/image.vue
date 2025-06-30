<template>
  <div>
    <v-form ref="domUrlForm" @submit.prevent="createRecipe">
      <div>
        <v-card-title class="headline">
          {{ $t("recipe.create-recipe-from-an-image") }}
        </v-card-title>
        <v-card-text>
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
            <div v-if="uploadedImages.length > 0" class="mt-3">
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
                  <ImageCropper
                    :img="imageUrl"
                    cropper-height="100%"
                    cropper-width="100%"
                    :submitted="loading"
                    class="mt-4"
                    @save="(croppedImage) => updateUploadedImage(index, croppedImage)"
                    @delete="clearImage(index)"
                  />
                </v-col>
              </v-row>
            </div>
          </v-container>
        </v-card-text>
        <v-card-actions v-if="uploadedImages.length">
          <div class="w-100 d-flex flex-column align-center">
            <p style="width: 250px">
              <BaseButton rounded block type="submit" :loading="loading" />
            </p>
            <p>
              <v-checkbox
                v-model="shouldTranslate"
                hide-details
                :label="$t('recipe.should-translate-description')"
                :disabled="loading"
              />
            </p>
            <p v-if="loading" class="mb-0">
              {{
                uploadedImages.length > 1
                  ? $t("recipe.please-wait-images-processing")
                  : $t("recipe.please-wait-image-procesing")
              }}
            </p>
          </div>
        </v-card-actions>
      </div>
    </v-form>
  </div>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import type { VForm } from "~/types/auto-forms";

export default defineNuxtComponent({
  setup() {
    const state = reactive({
      loading: false,
    });

    const i18n = useI18n();
    const api = useUserApi();
    const route = useRoute();
    const router = useRouter();
    const groupSlug = computed(() => route.params.groupSlug || "");

    const domUrlForm = ref<VForm | null>(null);
    const uploadedImages = ref<(Blob | File)[]>([]);
    const uploadedImageNames = ref<string[]>([]);
    const uploadedImagesPreviewUrls = ref<string[]>([]);
    const shouldTranslate = ref(true);

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

      uploadedImages.value = uploadedImages.value.filter((_, i) => i !== index);
      uploadedImageNames.value = uploadedImageNames.value.filter((_, i) => i !== index);
      uploadedImagesPreviewUrls.value = uploadedImagesPreviewUrls.value.filter((_, i) => i !== index);
    }

    async function createRecipe() {
      if (uploadedImages.value.length === 0) {
        return;
      }

      state.loading = true;
      const translateLanguage = shouldTranslate.value ? i18n.locale : undefined;
      const { data, error } = await api.recipes.createOneFromImages(uploadedImages.value, translateLanguage?.value);
      if (error || !data) {
        alert.error(i18n.t("events.something-went-wrong"));
        state.loading = false;
      }
      else {
        router.push(`/g/${groupSlug.value}/r/${data}`);
      }
    }

    function updateUploadedImage(index: number, croppedImage: Blob) {
      uploadedImages.value[index] = croppedImage;
      uploadedImagesPreviewUrls.value[index] = URL.createObjectURL(croppedImage);
    }

    return {
      ...toRefs(state),
      domUrlForm,
      uploadedImages,
      uploadedImagesPreviewUrls,
      shouldTranslate,
      uploadImages,
      clearImage,
      createRecipe,
      updateUploadedImage,
    };
  },
});
</script>
