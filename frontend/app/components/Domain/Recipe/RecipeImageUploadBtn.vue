<template>
  <div class="text-center">
    <BaseDialog
      v-model="dialogDeleteImage"
      bottom-sheet
      :title="$t('recipe.delete-image')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-delete
      @delete="deleteImage"
    >
      <v-card-text>
        {{ $t("recipe.delete-image-confirmation") }}
      </v-card-text>
    </BaseDialog>
    <BaseDialog
      v-model="imageDialog"
      bottom-sheet
      :title="$t('recipe.recipe-image')"
      :icon="$globals.icons.fileImage"
      :loading="loading"
      max-width="400"
    >
      <template #activator="{ open }">
        <v-btn
          color="accent"
          dark
          @click="open"
        >
          <v-icon start>
            {{ $globals.icons.fileImage }}
          </v-icon>
          {{ $t("general.image") }}
        </v-btn>
      </template>
      <v-card-text>
        <v-text-field
          v-model="url"
          :label="$t('general.url')"
          class="pt-2"
          clearable
          :messages="messages"
        >
          <template #append>
            <v-btn
              class="ml-2"
              color="primary"
              :loading="loading"
              :disabled="!slug"
              @click="getImageFromURL"
            >
              {{ $t("general.get") }}
            </v-btn>
          </template>
        </v-text-field>
      </v-card-text>
      <template #custom-card-action>
        <AppButtonUpload
          url="none"
          file-name="image"
          :text-btn="false"
          :post="false"
          @uploaded="uploadImage"
        />
        <BaseButton
          class="ml-2"
          delete
          @click="dialogDeleteImage = true"
        />
      </template>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { alertUnreportedError } from "~/composables/use-toast";
import { useUserApi } from "~/composables/api";

const UPLOAD_EVENT = "upload";
const DELETE_EVENT = "delete";
const REFRESH_EVENT = "refresh";

const props = defineProps<{ slug: string }>();

const emit = defineEmits<{
  refresh: [image: string];
  upload: [fileObject: File];
  delete: [];
}>();

const i18n = useI18n();
const api = useUserApi();

const url = ref("");
const loading = ref(false);
const imageDialog = ref(false);
const dialogDeleteImage = ref(false);

function uploadImage(fileObject: File) {
  emit(UPLOAD_EVENT, fileObject);
  imageDialog.value = false;
}

async function deleteImage() {
  loading.value = true;
  const { error } = await api.recipes.deleteImage(props.slug);
  loading.value = false;

  if (error) {
    alertUnreportedError(error, i18n.t("events.something-went-wrong"));
    return;
  }

  emit(DELETE_EVENT);
  imageDialog.value = false;
}

async function getImageFromURL() {
  loading.value = true;
  const { data, error } = await api.recipes.updateImagebyURL(props.slug, url.value);
  loading.value = false;

  if (error) {
    alertUnreportedError(error, i18n.t("events.something-went-wrong"));
    return;
  }

  if (data?.image) {
    emit(REFRESH_EVENT, data.image);
  }
  imageDialog.value = false;
}

const messages = computed(() =>
  props.slug ? [""] : [i18n.t("recipe.save-recipe-before-use")],
);
</script>

<style lang="scss" scoped></style>
