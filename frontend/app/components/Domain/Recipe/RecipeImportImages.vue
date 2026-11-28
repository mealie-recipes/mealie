<template>
  <div>
    <AppButtonUpload
      url="none"
      file-name="files"
      :accept="uploadAccept"
      :text="$t('recipe.import-with-ai-upload-files')"
      :text-btn="false"
      :post="false"
      :multiple="true"
      :disabled="disabled"
      @uploaded="handleFilesUploaded"
    />
    <p class="text-caption mt-1">
      {{ $t('recipe.import-with-ai-upload-files-hint') }}
    </p>
    <ul v-if="documents.length" class="mt-2">
      <li v-for="(file, index) in documents" :key="index">
        {{ file.name }}
        <v-btn
          icon
          size="x-small"
          variant="text"
          :disabled="disabled"
          @click="removeDocument(index)"
        >
          <v-icon size="small">
            {{ $globals.icons.close }}
          </v-icon>
        </v-btn>
      </li>
    </ul>
    <div v-if="images.length" class="mt-6">
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
import { alert } from "~/composables/use-toast";

// keep in sync with the extensions handled by mealie/services/recipe/document_text_extraction.py
const DOCUMENT_EXTENSIONS = [".pdf", ".docx", ".odt", ".md", ".txt", ".rtf", ".html"];
const IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".avif", ".heic", ".heif", ".tif", ".tiff"];

const props = withDefaults(defineProps<{
  disabled?: boolean;
  imagesEnabled?: boolean;
}>(), {
  disabled: false,
  imagesEnabled: true,
});

const images = defineModel<(Blob | File)[]>({ default: () => [] });
const documents = defineModel<File[]>("documents", { default: () => [] });

const i18n = useI18n();

const previewUrls = ref<string[]>([]);

const uploadAccept = computed(() => {
  const accept = [...DOCUMENT_EXTENSIONS];
  if (props.imagesEnabled) {
    accept.push("image/*");
  }
  return accept.join(",");
});

function isDocumentFile(file: File): boolean {
  const name = file.name.toLowerCase();
  return DOCUMENT_EXTENSIONS.some(extension => name.endsWith(extension));
}

function isImageFile(file: File): boolean {
  const name = file.name.toLowerCase();
  return file.type.startsWith("image/") || IMAGE_EXTENSIONS.some(extension => name.endsWith(extension));
}

function handleFilesUploaded(files: File[]) {
  const newDocumentFiles: File[] = [];
  const newImageFiles: File[] = [];

  for (const file of files) {
    if (isDocumentFile(file)) {
      newDocumentFiles.push(file);
    }
    else if (isImageFile(file) && props.imagesEnabled) {
      newImageFiles.push(file);
    }
    else if (!isImageFile(file)) {
      const key = file.name.toLowerCase().endsWith(".doc")
        ? "recipe.import-with-ai-unsupported-file"
        : "recipe.import-with-ai-unsupported-file-generic";
      alert.error(i18n.t(key, { name: file.name }));
    }
  }

  if (newDocumentFiles.length) {
    documents.value = [...documents.value, ...newDocumentFiles];
  }
  if (newImageFiles.length) {
    uploadImages(newImageFiles);
  }
}

function removeDocument(index: number) {
  documents.value.splice(index, 1);
}

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
