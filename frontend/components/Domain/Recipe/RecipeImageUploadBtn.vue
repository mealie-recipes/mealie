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
        <v-card-title class="headline flex mb-0">
          <div>
            {{ $t("recipe.recipe-image") }}
          </div>
          <AppButtonUpload
            class="ml-auto"
            url="none"
            file-name="image"
            :text-btn="false"
            :post="false"
            @uploaded="uploadImage"
          />
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
import { useUserApi } from "~/composables/api";

const REFRESH_EVENT = "refresh";
const UPLOAD_EVENT = "upload";

const props = defineProps<{ slug: string }>();

const emit = defineEmits<{
  refresh: [];
  upload: [fileObject: File];
}>();

const url = ref("");
const loading = ref(false);
const menu = ref(false);

function uploadImage(fileObject: File) {
  emit(UPLOAD_EVENT, fileObject);
  menu.value = false;
}

const api = useUserApi();
async function getImageFromURL() {
  loading.value = true;
  if (await api.recipes.updateImagebyURL(props.slug, url.value)) {
    emit(REFRESH_EVENT);
  }
  loading.value = false;
  menu.value = false;
}

const i18n = useI18n();
const messages = computed(() =>
  props.slug ? [""] : [i18n.t("recipe.save-recipe-before-use")],
);
</script>

<style lang="scss" scoped></style>
