<template>
  <div>
    <v-card-title class="headline pb-3">
      <v-icon class="mr-2">
        {{ $globals.icons.commentTextMultipleOutline }}
      </v-icon>
      {{ $t("recipe.comments") }}
    </v-card-title>
    <v-divider class="mx-2"></v-divider>
    <div v-if="user.id" class="d-flex flex-column">
      <div class="d-flex mt-3" style="gap: 10px">
        <UserAvatar size="40" :user-id="user.id" />

        <v-textarea
          v-model="comment"
          hide-details=""
          dense
          single-line
          outlined
          auto-grow
          rows="2"
          :placeholder="$t('recipe.join-the-conversation')"
        >
        </v-textarea>
      </div>
      <div class="ml-auto mt-1">
        <BaseButton small :disabled="!comment" @click="submitComment">
          <template #icon>{{ $globals.icons.check }}</template>
          {{ $t("general.submit") }}
        </BaseButton>
      </div>
    </div>
    <div v-for="comment in comments" :key="comment.id" class="d-flex my-2" style="gap: 10px">
      <UserAvatar size="40" :user-id="comment.userId" />
      <v-card outlined class="flex-grow-1">
        <v-card-text class="pa-3 pb-0">
          <p class="">{{ comment.user.username }} • {{ $d(Date.parse(comment.createdAt), "medium") }}</p>
          {{ comment.text }}
        </v-card-text>
        <v-card-actions class="justify-end mt-0 pt-0">
          <v-btn
            v-if="user.id == comment.user.id || user.admin"
            color="error"
            text
            x-small
            @click="deleteComment(comment.id)"
          >
            {{ $t("general.delete") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, toRefs, onMounted, reactive } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { Recipe, RecipeCommentOut } from "~/lib/api/types/recipe";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { usePageUser } from "~/composables/recipe-page/shared-state";

export default defineComponent({
  components: {
    UserAvatar,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const api = useUserApi();

    const comments = ref<RecipeCommentOut[]>([]);

    const { user } = usePageUser();

    const state = reactive({
      comment: "",
    });

    onMounted(async () => {
      const { data } = await api.recipes.comments.byRecipe(props.recipe.slug);

      if (data) {
        comments.value = data;
      }
    });

    async function submitComment() {
      const { data } = await api.recipes.comments.createOne({
        recipeId: props.recipe.id,
        text: state.comment,
      });

      if (data) {
        comments.value.push(data);
      }

      state.comment = "";
    }

    async function deleteComment(id: string) {
      const { response } = await api.recipes.comments.deleteOne(id);

      if (response?.status === 200) {
        comments.value = comments.value.filter((comment) => comment.id !== id);
      }
    }

    return { api, comments, ...toRefs(state), submitComment, deleteComment, user };
  },
});
</script>
