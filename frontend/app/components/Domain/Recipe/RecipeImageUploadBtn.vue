<template>
  <div class="text-center">
    <v-menu
      v-model="menu"
      offset-y
      top
      nudge-top="6"
      :close-on-content-click="false"
    >
      <template #activator="{ props: activatorProps }">
        <v-btn
          color="accent"
          dark
          v-bind="activatorProps"
        >
          <v-icon start>
            {{ $globals.icons.fileImage }}
          </v-icon>
          {{ $t("general.image") }}
        </v-btn>
      </template>
      <v-card width="400">
        <v-card-title class="headline flex-wrap mb-0">
          <div>
            {{ $t("recipe.recipe-image") }}
          </div>
          <div class="d-flex gap-2">
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
            <BaseDialog
              v-model="dialogDeleteImage"
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
          </div>
        </v-card-title>
        <v-card-text class="mt-n5">
          <div>
            <v-text-field
              v-model="url"
              :label="$t('general.url')"
              class="pt-5"
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
          </div>
        </v-card-text>
      </v-card>
    </v-menu>
  </div>
</template>

<script setup lang="ts">
import { alert } from "~/composables/use-toast";
import { useUserApi } from "~/composables/api";

const UPLOAD_EVENT = "upload";
const DELETE_EVENT = "delete";

const props = defineProps<{ slug: string }>();

const emit = defineEmits<{
  refresh: [];
  upload: [fileObject: File];
  delete: [];
}>();

const i18n = useI18n();
const api = useUserApi();

const url = ref("");
const loading = ref(false);
const menu = ref(false);
const dialogDeleteImage = ref(false);

function uploadImage(fileObject: File) {
  emit(UPLOAD_EVENT, fileObject);
  menu.value = false;
}

async function deleteImage() {
  loading.value = true;
  try {
    await api.recipes.deleteImage(props.slug);
    emit(DELETE_EVENT);
    menu.value = false;
  }
  catch (e) {
    alert.error(i18n.t("events.something-went-wrong"));
    console.error("Failed to delete image", e);
  }
  finally {
    loading.value = false;
  }
}

async function getImageFromURL() {
  loading.value = true;
  if (await api.recipes.updateImagebyURL(props.slug, url.value)) {
    emit(DELETE_EVENT);
  }
  loading.value = false;
  menu.value = false;
}

const messages = computed(() =>
  props.slug ? [""] : [i18n.t("recipe.save-recipe-before-use")],
);
</script>

<style lang="scss" scoped></style>
