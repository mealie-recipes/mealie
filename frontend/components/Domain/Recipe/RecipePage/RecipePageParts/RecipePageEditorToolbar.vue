<template>
  <div class="d-flex justify-start align-top flex-wrap">
    <RecipeImageUploadBtn
      class="my-2"
      :slug="recipe.slug"
      @upload="uploadImage"
      @refresh="imageKey++"
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
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import RecipeImageUploadBtn from "~/components/Domain/Recipe/RecipeImageUploadBtn.vue";
import RecipeSettingsMenu from "~/components/Domain/Recipe/RecipeSettingsMenu.vue";
import { useUserStore } from "~/composables/store/use-user-store";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import { useHouseholdStore } from "~/composables/store";

const recipe = defineModel<NoUndefinedField<Recipe>>({ required: true });

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
  const newVersion = await api.recipes.updateImage(recipe.value.slug, fileObject);
  if (newVersion?.data?.image) {
    recipe.value.image = newVersion.data.image;
  }
  imageKey.value++;
}
</script>
