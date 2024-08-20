<template>
  <div>
    <v-form ref="domUrlForm" @submit.prevent="createRecipe">
      <div>
        <v-card-title class="headline"> {{ $t('recipe.create-recipe-from-an-image') }} </v-card-title>
        <v-card-text>
          <p>{{ $t('recipe.create-recipe-from-an-image-description') }}</p>
          <v-container class="pa-0">
            <v-row>
              <v-col cols="auto" align-self="center">
                <AppButtonUpload
                  v-if="!uploadedImage"
                  class="ml-auto"
                  url="none"
                  file-name="image"
                  accept="image/*"
                  :text="$i18n.tc('recipe.upload-image')"
                  :text-btn="false"
                  :post="false"
                  @uploaded="uploadImage"
                />
                <v-btn
                  v-if="!!uploadedImage"
                  color="error"
                  @click="clearImage"
                >
                  <v-icon left>{{ $globals.icons.close }}</v-icon>
                  {{ $i18n.tc('recipe.remove-image') }}
                </v-btn>
              </v-col>
              <v-spacer />
            </v-row>

            <div v-if="uploadedImage && uploadedImagePreviewUrl" class="mt-3">
              <v-row>
                <v-col cols="12" class="pb-0">
                  <v-card-text class="pa-0">
                    <p class="mb-0">
                      {{ $t('recipe.crop-and-rotate-the-image') }}
                    </p>
                  </v-card-text>
                </v-col>
              </v-row>
              <v-row style="max-width: 600px;">
                <v-spacer />
                <v-col cols="12">
                  <ImageCropper
                    :img="uploadedImagePreviewUrl"
                    cropper-height="50vh"
                    cropper-width="100%"
                    @save="updateUploadedImage"
                  />
                </v-col>
                <v-spacer />
              </v-row>
            </div>
          </v-container>
        </v-card-text>
        <v-card-actions v-if="uploadedImage">
          <div>
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
              {{ $t('recipe.please-wait-image-procesing') }}
            </p>
          </div>
        </v-card-actions>
      </div>
    </v-form>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  ref,
  toRefs,
  useContext,
  useRoute,
  useRouter,
} from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { VForm } from "~/types/vuetify";

export default defineComponent({
  setup() {
    const state = reactive({
      loading: false,
    });

    const { i18n } = useContext();
    const api = useUserApi();
    const route = useRoute();
    const router = useRouter();
    const groupSlug = computed(() => route.value.params.groupSlug || "");

    const domUrlForm = ref<VForm | null>(null);
    const uploadedImage = ref<Blob | File>();
    const uploadedImageName = ref<string>("");
    const uploadedImagePreviewUrl = ref<string>();
    const shouldTranslate = ref(true);

    function uploadImage(fileObject: File) {
      uploadedImage.value = fileObject;
      uploadedImageName.value = fileObject.name;
      uploadedImagePreviewUrl.value = URL.createObjectURL(fileObject);
    }

    function updateUploadedImage(fileObject: Blob) {
      uploadedImage.value = fileObject;
      uploadedImagePreviewUrl.value = URL.createObjectURL(fileObject);
    }

    function clearImage() {
      uploadedImage.value = undefined;
      uploadedImageName.value = "";
      uploadedImagePreviewUrl.value = undefined;
    }

    async function createRecipe() {
      if (!uploadedImage.value) {
        return;
      }

      state.loading = true;
      const translateLanguage = shouldTranslate.value ? i18n.locale : undefined;
      const { data, error } = await api.recipes.createOneFromImage(uploadedImage.value, uploadedImageName.value, translateLanguage);
      if (error || !data) {
        alert.error(i18n.tc("events.something-went-wrong"));
        state.loading = false;
      } else {
        router.push(`/g/${groupSlug.value}/r/${data}`);
      };
    }

    return {
      ...toRefs(state),
      domUrlForm,
      uploadedImage,
      uploadedImagePreviewUrl,
      shouldTranslate,
      uploadImage,
      updateUploadedImage,
      clearImage,
      createRecipe,
    };
  },
});
</script>
