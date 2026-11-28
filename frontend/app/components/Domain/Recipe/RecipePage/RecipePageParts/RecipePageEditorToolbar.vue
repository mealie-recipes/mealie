<template>
  <div class="d-flex justify-start align-top flex-wrap">
    <RecipeImageUploadBtn
      class="my-2"
      :slug="recipe.slug"
      @upload="uploadImage"
      @clipboard="previewPastedImage"
      @refresh="refreshImage"
      @delete="deleteImage"
    />
    <RecipeSettingsMenu
      v-model="recipe.settings"
      class="my-2 mx-1"
      :is-owner="recipe.userId == user.id"
      @upload="uploadImage"
    />
    <v-spacer />
    <v-select
      v-model="recipe.userId"
      class="my-2"
      max-width="300"
      :items="allUsers"
      :item-props="itemsProps"
      :label="$t('general.owner')"
      :disabled="!canEditOwner"
      variant="outlined"
      density="compact"
    >
      <template #prepend>
        <UserAvatar
          :user-id="recipe.userId"
          :tooltip="false"
        />
      </template>
    </v-select>
    <BaseDialog
      v-model="pasteDialog"
      :title="$t('recipe.paste-image-title')"
      :icon="$globals.icons.fileImage"
      can-confirm
      @confirm="confirmPastedImage"
      @close="clearPastedImage"
    >
      <v-card-text>
        <p>{{ $t("recipe.paste-image-description") }}</p>
        <v-img
          v-if="pastedImageUrl"
          :src="pastedImageUrl"
          max-height="300"
          class="mt-4"
        />
      </v-card-text>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import type { RecipeOut } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import RecipeImageUploadBtn from "~/components/Domain/Recipe/RecipeImageUploadBtn.vue";
import RecipeSettingsMenu from "~/components/Domain/Recipe/RecipeSettingsMenu.vue";
import { useUserStore } from "~/composables/store/use-user-store";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import { useHouseholdStore } from "~/composables/store";
import { usePasteImage } from "~/composables/use-paste-image";

const recipe = defineModel<RecipeOut>({ required: true });

const { user } = usePageUser();
const api = useUserApi();
const { imageKey } = usePageState(recipe.value.slug);

const canEditOwner = computed(() => {
  return user.id === recipe.value.userId || user.admin;
});

const { store: allUsers } = useUserStore();
const { store: households } = useHouseholdStore();

function itemsProps(item: any) {
  const owner = allUsers.value.find(u => u.id === item.id);
  return {
    value: item.id,
    title: item.fullName,
    subtitle: owner ? households.value.find(h => h.id === owner.householdId)?.name || "" : "",
  };
}

async function uploadImage(fileObject: File) {
  if (!recipe.value || !recipe.value.slug) {
    return;
  }
  const { data, error } = await api.recipes.updateImage(recipe.value.slug, fileObject);
  if (error) {
    return;
  }

  if (data?.image) {
    recipe.value.image = data.image;
  }
  imageKey.value++;
}

// The toolbar only exists while editing, so pasting an image only works in edit mode.
const pasteDialog = ref(false);
const pastedImage = ref<File | null>(null);
const pastedImageUrl = ref("");

function clearPastedImage() {
  URL.revokeObjectURL(pastedImageUrl.value);
  pastedImage.value = null;
  pastedImageUrl.value = "";
}

// The dialog closes on confirm, so without this a second paste could race the first upload
const uploadingPastedImage = ref(false);

function previewPastedImage(file: File) {
  if (uploadingPastedImage.value) {
    return;
  }

  clearPastedImage();
  pastedImage.value = file;
  pastedImageUrl.value = URL.createObjectURL(file);
  pasteDialog.value = true;
}

usePasteImage({
  onImage: previewPastedImage,
  enabled: () => !uploadingPastedImage.value,
});

async function confirmPastedImage() {
  if (!pastedImage.value) {
    return;
  }

  uploadingPastedImage.value = true;
  try {
    await uploadImage(pastedImage.value);
  }
  finally {
    uploadingPastedImage.value = false;
  }
}

onBeforeUnmount(clearPastedImage);

function refreshImage(image: string) {
  if (image) {
    recipe.value.image = image;
  }
  imageKey.value++;
}

async function deleteImage() {
  // The image is already deleted on the backend, just need to update the UI
  recipe.value.image = "";
  imageKey.value++;
}
</script>
