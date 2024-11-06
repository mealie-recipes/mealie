<template>
  <div class="d-flex justify-start align-top py-2">
    <RecipeImageUploadBtn class="my-1" :slug="recipe.slug" @upload="uploadImage" @refresh="imageKey++" />
    <RecipeSettingsMenu
      class="my-1 mx-1"
      :value="recipe.settings"
      :is-owner="recipe.userId == user.id"
      @upload="uploadImage"
    />
    <v-spacer />
    <v-container class="py-0" style="width: 40%;">
      <v-select
        v-model="recipe.userId"
        :items="allUsers"
        item-text="fullName"
        item-value="id"
        :label="$tc('general.owner')"
        hide-details
        :disabled="!canEditOwner"
      >
        <template #prepend>
          <UserAvatar :user-id="recipe.userId" :tooltip="false" />
        </template>
      </v-select>
      <v-card-text v-if="ownerHousehold" class="pa-0 d-flex" style="align-items: flex-end;">
        <v-spacer />
        <v-icon>{{ $globals.icons.household }}</v-icon>
        <span class="pl-1">{{ ownerHousehold.name }}</span>
      </v-card-text>
    </v-container>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import RecipeImageUploadBtn from "~/components/Domain/Recipe/RecipeImageUploadBtn.vue";
import RecipeSettingsMenu from "~/components/Domain/Recipe/RecipeSettingsMenu.vue";
import { useUserStore } from "~/composables/store/use-user-store";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import { useHouseholdStore } from "~/composables/store";

export default defineComponent({
  components: {
    RecipeImageUploadBtn,
    RecipeSettingsMenu,
    UserAvatar,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const { user } = usePageUser();
    const api = useUserApi();
    const { imageKey } = usePageState(props.recipe.slug);

    const canEditOwner = computed(() => {
      return user.id === props.recipe.userId || user.admin;
    })

    const { store: allUsers } = useUserStore();
    const { store: households } = useHouseholdStore();
    const ownerHousehold = computed(() => {
      const owner = allUsers.value.find((u) => u.id === props.recipe.userId);
      if (!owner) {
        return null;
      };

      return households.value.find((h) => h.id === owner.householdId);
    });

    async function uploadImage(fileObject: File) {
      if (!props.recipe || !props.recipe.slug) {
        return;
      }
      const newVersion = await api.recipes.updateImage(props.recipe.slug, fileObject);
      if (newVersion?.data?.image) {
        props.recipe.image = newVersion.data.image;
      }
      imageKey.value++;
    }

    return {
      user,
      canEditOwner,
      uploadImage,
      imageKey,
      allUsers,
      ownerHousehold,
    };
  },
});
</script>
