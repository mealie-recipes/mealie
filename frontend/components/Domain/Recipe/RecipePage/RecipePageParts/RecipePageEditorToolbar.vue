<template>
  <div class="d-flex justify-start align-top py-2">
    <RecipeImageUploadBtn
      class="my-1"
      :slug="recipe.slug"
      @upload="uploadImage"
      @refresh="imageKey++"
    />
    <RecipeSettingsMenu
      v-model="recipe.settings"
      class="my-1 mx-1"
      :is-owner="recipe.userId == user.id"
      @upload="uploadImage"
    />
    <v-spacer />
    <v-container
      class="py-0"
      style="width: 40%;"
    >
      <v-select
        v-model="recipe.userId"
        :items="allUsers"
        item-title="fullName"
        item-value="id"
        :label="$t('general.owner')"
        hide-details
        :disabled="!canEditOwner"
        variant="underlined"
      >
        <template #prepend>
          <UserAvatar
            :user-id="recipe.userId"
            :tooltip="false"
          />
        </template>
      </v-select>
      <v-card-text
        v-if="ownerHousehold"
        class="pa-0 d-flex"
        style="align-items: flex-end;"
      >
        <v-spacer />
        <v-icon>{{ $globals.icons.household }}</v-icon>
        <span class="pl-1">{{ ownerHousehold.name }}</span>
      </v-card-text>
    </v-container>
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
const ownerHousehold = computed(() => {
  const owner = allUsers.value.find(u => u.id === recipe.value.userId);
  if (!owner) {
    return null;
  }
  return households.value.find(h => h.id === owner.householdId);
});

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
