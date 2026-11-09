<template>
  <section
    v-if="photos.length || canEdit"
    class="pa-4 d-print-none"
    :aria-label="$t('recipe.photos')"
    @dragover.prevent
    @drop.prevent="onDrop"
  >
    <div class="d-flex align-center flex-wrap ga-2 mb-2">
      <h2 class="text-h6">
        {{ $t('recipe.photos') }}
      </h2>
      <v-spacer />
      <v-btn
        v-if="canEdit"
        color="primary"
        variant="tonal"
        :loading="busy"
        @click="uploader?.click()"
      >
        <v-icon start>
          {{ $globals.icons.create }}
        </v-icon>
        {{ $t('recipe.add-photos') }}
      </v-btn>
      <input
        v-if="canEdit"
        ref="uploader"
        type="file"
        class="d-none"
        :accept="RECIPE_PHOTO_ACCEPT"
        :disabled="busy"
        multiple
        :aria-label="$t('recipe.add-photos')"
        @change="onFilesSelected"
      >
    </div>
    <p v-if="canEdit" class="text-body-2 text-medium-emphasis mb-3">
      {{ $t('recipe.add-photos-hint') }}
    </p>
    <div class="d-flex ga-3 overflow-x-auto pb-2">
      <v-card v-for="(photo, index) in photos" :key="photo.fileName ?? photo.name" width="144" class="flex-shrink-0">
        <button
          type="button"
          class="photo-preview"
          :aria-label="$t('recipe.view-photo', { name: photo.name })"
          @click="openPhoto(index)"
        >
          <v-img :src="assetURL(photo)" :alt="photo.name" height="104" cover loading="lazy" />
        </button>
        <div class="d-flex align-center pl-2">
          <span class="text-body-2 text-truncate">{{ photo.name }}</span>
          <v-menu>
            <template #activator="{ props: menuProps }">
              <v-btn
                v-bind="menuProps"
                :icon="$globals.icons.dotsVertical"
                variant="text"
                size="small"
                :disabled="busy"
                :aria-label="$t('recipe.photo-actions', { name: photo.name })"
              />
            </template>
            <v-list density="compact">
              <v-list-item :title="$t('general.view')" @click="openPhoto(index)" />
              <v-list-item :title="$t('general.download')" :href="assetURL(photo)" download />
              <v-list-item v-if="canEdit" :title="$t('recipe.set-as-cover')" @click="setCover(photo)" />
              <v-list-item v-if="canEdit" :title="$t('general.delete')" @click="pendingDelete = photo" />
            </v-list>
          </v-menu>
        </div>
      </v-card>
    </div>
    <RecipeImageLightbox
      v-if="selectedPhoto"
      v-model="lightboxOpen"
      :image-url="assetURL(selectedPhoto)"
      :image-alt="selectedPhoto.name"
      :navigation="photos.length > 1"
      @previous="movePhoto(-1)"
      @next="movePhoto(1)"
    />
    <BaseDialog
      :model-value="!!pendingDelete"
      :title="$t('recipe.delete-image')"
      color="error"
      can-delete
      @update:model-value="!$event && (pendingDelete = null)"
      @delete="deletePhoto"
    >
      <v-card-text>{{ $t('recipe.delete-photo-confirmation') }}</v-card-text>
    </BaseDialog>
  </section>
</template>

<script setup lang="ts">
import { useStaticRoutes, useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { usePageState } from "~/composables/recipe-page/shared-state";
import type { RecipeAsset, RecipeOut } from "~/lib/api/types/recipe";
import { isRecipePhoto, RECIPE_PHOTO_ACCEPT } from "~/lib/recipe/photos";
import RecipeImageLightbox from "./RecipeImageLightbox.vue";

const props = defineProps<{ canEdit: boolean }>();
const recipe = defineModel<RecipeOut>({ required: true });
const emit = defineEmits<{ saved: []; busy: [value: boolean] }>();
const api = useUserApi();
const { recipeAssetPath } = useStaticRoutes();
const { imageKey } = usePageState(recipe.value.slug);
const i18n = useI18n();
const uploader = ref<HTMLInputElement>();
const busy = ref(false);
const photos = computed(() => recipe.value.assets.filter(asset => isRecipePhoto(asset.fileName)));
const selectedIndex = ref(0);
const lightboxOpen = ref(false);
const selectedPhoto = computed(() => photos.value[selectedIndex.value]);
const pendingDelete = ref<RecipeAsset | null>(null);

watch(busy, value => emit("busy", value), { flush: "sync" });

function assetURL(photo: RecipeAsset) {
  return recipeAssetPath(recipe.value.id, photo.fileName ?? "");
}

function openPhoto(index: number) {
  selectedIndex.value = index;
  lightboxOpen.value = true;
}

function movePhoto(offset: number) {
  selectedIndex.value = (selectedIndex.value + offset + photos.value.length) % photos.value.length;
}

function onFilesSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  const files = Array.from(input.files ?? []);
  input.value = "";
  void uploadPhotos(files);
}

function onDrop(event: DragEvent) {
  void uploadPhotos(Array.from(event.dataTransfer?.files ?? []));
}

async function uploadPhotos(files: File[]) {
  if (!props.canEdit || busy.value || !files.length) return;
  busy.value = true;
  try {
    for (const file of files) {
      if (!isRecipePhoto(file.name)) {
        alert.error(i18n.t("recipe.photo-upload-invalid", { name: file.name }));
        continue;
      }
      try {
        const { data, error } = await api.recipes.createAsset(recipe.value.slug, {
          file,
          name: file.name.replace(/\.[^.]+$/, ""),
          icon: "mdi-file-image",
          extension: file.name.split(".").pop()!.toLowerCase(),
        });
        if (error || !data) throw new Error("Photo upload failed");
        recipe.value.assets = [...recipe.value.assets, data];
        emit("saved");
      }
      catch {
        alert.error(i18n.t("recipe.photo-upload-failed", { name: file.name }));
      }
    }
  }
  finally {
    busy.value = false;
  }
}

async function setCover(photo: RecipeAsset) {
  if (!props.canEdit || busy.value) return;
  busy.value = true;
  try {
    const response = await fetch(assetURL(photo));
    if (!response.ok) throw new Error("Photo download failed");
    const file = new File([await response.blob()], photo.fileName ?? "photo.jpg");
    const { data, error } = await api.recipes.updateImage(recipe.value.slug, file);
    if (error || !data?.image) throw new Error("Cover update failed");
    recipe.value.image = data.image;
    imageKey.value++;
    emit("saved");
  }
  catch {
    alert.error(i18n.t("recipe.photo-cover-failed"));
  }
  finally {
    busy.value = false;
  }
}

async function deletePhoto() {
  const photo = pendingDelete.value;
  pendingDelete.value = null;
  if (!photo || !props.canEdit || busy.value) return;
  busy.value = true;
  try {
    const current = await api.recipes.getOne(recipe.value.slug);
    if (current.error || !current.data) throw new Error("Recipe load failed");
    const assets = current.data.assets.filter(asset => asset.fileName !== photo.fileName);
    const { data, error } = await api.recipes.patchOne(recipe.value.slug, { assets });
    if (error || !data) throw new Error("Photo delete failed");
    recipe.value.assets = data.assets;
    lightboxOpen.value = false;
    selectedIndex.value = 0;
    emit("saved");
  }
  catch {
    alert.error(i18n.t("recipe.photo-delete-failed"));
  }
  finally {
    busy.value = false;
  }
}
</script>

<style scoped>
.photo-preview {
  display: block;
  width: 100%;
  cursor: zoom-in;
}
</style>
