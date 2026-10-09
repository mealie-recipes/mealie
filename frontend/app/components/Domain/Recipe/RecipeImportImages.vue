<template>
  <div>
    <AppButtonUpload
      class="ml-auto"
      url="none"
      file-name="images"
      accept="image/*"
      :text="images.length ? $t('recipe.upload-more-images') : $t('recipe.upload-images')"
      :text-btn="false"
      :post="false"
      :multiple="true"
      :disabled="disabled"
      @uploaded="uploadImages"
    />
    <div v-if="images.length" class="mt-3">
      <p class="my-2">
        {{ $t("recipe.crop-and-rotate-the-image") }}
      </p>
      <v-row>
        <v-col
          v-for="(imageUrl, index) in previewUrls"
          :key="index"
          cols="12"
          sm="6"
          lg="4"
          xl="3"
        >
          <v-col>
            <ImageCropper
              :img="imageUrl"
              cropper-width="100%"
              :submitted="disabled"
              class="mt-4 mb-2"
              @save="(croppedImage: Blob) => updateImage(index, croppedImage)"
              @delete="clearImage(index)"
            />

            <v-btn
              v-if="images.length > 1"
              :disabled="disabled || index === 0"
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
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  disabled?: boolean;
}>(), {
  disabled: false,
});

const images = defineModel<(Blob | File)[]>({ default: () => [] });

const previewUrls = ref<string[]>([]);

function uploadImages(files: File[]) {
  images.value = [...images.value, ...files];
  previewUrls.value = [...previewUrls.value, ...files.map(file => URL.createObjectURL(file))];
}

function clearImage(index: number) {
  // Revoke _before_ splicing
  URL.revokeObjectURL(previewUrls.value[index]);

  images.value.splice(index, 1);
  previewUrls.value.splice(index, 1);
}

function updateImage(index: number, croppedImage: Blob) {
  images.value[index] = croppedImage;
  previewUrls.value[index] = URL.createObjectURL(croppedImage);
}

function swapItem(array: any[], i: number, j: number) {
  if (i < 0 || j < 0 || i >= array.length || j >= array.length) {
    return;
  }

  const temp = array[i];
  array[i] = array[j];
  array[j] = temp;
}

// Put the intended cover image at the start of the array.
// The backend uses the first image as the cover image.
function setCoverImage(index: number) {
  if (index < 0 || index >= images.value.length || index === 0) {
    return;
  }

  swapItem(images.value, 0, index);
  swapItem(previewUrls.value, 0, index);
}

onBeforeUnmount(() => {
  previewUrls.value.forEach(url => URL.revokeObjectURL(url));
});
</script>
