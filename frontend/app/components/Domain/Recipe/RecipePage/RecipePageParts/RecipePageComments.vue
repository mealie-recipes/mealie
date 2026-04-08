<template>
  <div>
    <v-card-title class="headline pb-3">
      <v-icon class="mr-2">
        {{ $globals.icons.commentTextMultipleOutline }}
      </v-icon>
      {{ $t("recipe.comments") }}
    </v-card-title>
    <v-divider class="mx-2" />
    <div
      v-if="user.id"
      class="d-flex flex-column"
    >
      <div
        class="d-flex mt-3"
        style="gap: 10px"
      >
        <UserAvatar
          :tooltip="false"
          size="40"
          :user-id="user.id"
        />

        <v-textarea
          v-model="comment"
          hide-details
          density="compact"
          single-line
          variant="outlined"
          auto-grow
          rows="2"
          :placeholder="$t('recipe.join-the-conversation')"
        />
      </div>
      <div class="ml-auto mt-1">
        <BaseButton
          size="small"
          :disabled="!comment"
          @click="submitComment"
        >
          <template #icon>
            {{ $globals.icons.check }}
          </template>
          {{ $t("general.submit") }}
        </BaseButton>
      </div>
    </div>
    <div
      v-for="recipeComment in recipe.comments"
      :key="recipeComment.id"
      class="d-flex my-2"
      style="gap: 10px"
    >
      <UserAvatar
        :tooltip="false"
        size="40"
        :user-id="recipeComment.userId"
      />
      <v-card
        variant="outlined"
        class="flex-grow-1"
      >
        <v-card-text class="pa-3 pb-0">
          <p class="">
            {{ recipeComment.user.fullName }} • {{ $d(Date.parse(recipeComment.createdAt), "medium") }}
          </p>
          <SafeMarkdown :source="recipeComment.text" />
        </v-card-text>
        <v-card-actions class="justify-end mt-0 pt-0">
          <v-btn
            v-if="user.id == recipeComment.user.id || user.admin"
            color="error"
            variant="text"
            size="x-small"
            @click="deleteComment(recipeComment.id)"
          >
            {{ $t("general.delete") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useUserApi } from "~/composables/api";
import type { Recipe } from "~/lib/api/types/recipe";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import { usePageUser } from "~/composables/recipe-page/shared-state";
import SafeMarkdown from "~/components/global/SafeMarkdown.vue";

const recipe = defineModel<NoUndefinedField<Recipe>>({ required: true });
const api = useUserApi();
const { user } = usePageUser();
const comment = ref("");

async function submitComment() {
  const { data } = await api.recipes.comments.createOne({
    recipeId: recipe.value.id,
    text: comment.value,
  });

  if (data) {
    recipe.value.comments.push(data);
  }

  comment.value = "";
}

async function deleteComment(id: string) {
  const { response } = await api.recipes.comments.deleteOne(id);

  if (response?.status === 200) {
    recipe.value.comments = recipe.value.comments.filter(comment => comment.id !== id);
  }
}
</script>
