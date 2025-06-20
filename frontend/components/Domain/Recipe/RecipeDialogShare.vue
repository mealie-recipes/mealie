<template>
  <div>
    <BaseDialog
      v-model="dialog"
      :title="$t('recipe-share.share-recipe')"
      :icon="$globals.icons.link"
    >
      <v-card-text>
        <v-menu
          v-model="datePickerMenu"
          :close-on-content-click="false"
          transition="scale-transition"
          offset-y
          max-width="290px"
          min-width="auto"
        >
          <template #activator="{ props }">
            <v-text-field
              v-model="expirationDateString"
              :label="$t('recipe-share.expiration-date')"
              :hint="$t('recipe-share.default-30-days')"
              persistent-hint
              :prepend-icon="$globals.icons.calendar"
              v-bind="props"
              readonly
            />
          </template>
          <v-date-picker
            v-model="expirationDate"
            hide-header
            :first-day-of-week="firstDayOfWeek"
            :local="$i18n.locale"
            @update:model-value="datePickerMenu = false"
          />
        </v-menu>
      </v-card-text>
      <v-card-actions class="justify-end">
        <BaseButton
          size="small"
          @click="createNewToken"
        >
          {{ $t("general.new") }}
        </BaseButton>
      </v-card-actions>

      <v-list-item
        v-for="token in tokens"
        :key="token.id"
        class="px-2"
        style="padding-top: 8px; padding-bottom: 8px;"
        @click="shareRecipe(token.id)"
      >
        <div class="d-flex align-center" style="width: 100%;">
          <v-avatar color="grey">
            <v-icon>
              {{ $globals.icons.link }}
            </v-icon>
          </v-avatar>

          <div class="pl-3 flex-grow-1">
            <v-list-item-title>
              {{ $t("recipe-share.expires-at") }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ $d(new Date(token.expiresAt!), "long") }}
            </v-list-item-subtitle>
          </div>

          <v-btn
            icon
            variant="text"
            class="ml-2"
            @click.stop="deleteToken(token.id)"
          >
            <v-icon color="error-lighten-1">
              {{ $globals.icons.delete }}
            </v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            class="ml-2"
            @click.stop="copyTokenLink(token.id)"
          >
            <v-icon color="info-lighten-1">
              {{ $globals.icons.contentCopy }}
            </v-icon>
          </v-btn>
        </div>
      </v-list-item>
    </BaseDialog>
  </div>
</template>

<script lang="ts">
import { useClipboard, useShare, whenever } from "@vueuse/core";
import type { RecipeShareToken } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import { useHouseholdSelf } from "~/composables/use-households";
import { alert } from "~/composables/use-toast";

export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
    recipeId: {
      type: String,
      required: true,
    },
    name: {
      type: String,
      required: true,
    },
  },
  emits: ["update:modelValue"],
  setup(props, context) {
    // V-Model Support
    const dialog = computed({
      get: () => {
        return props.modelValue;
      },
      set: (val) => {
        context.emit("update:modelValue", val);
      },
    });

    const state = reactive({
      datePickerMenu: false,
      expirationDate: new Date(Date.now() - new Date().getTimezoneOffset() * 60000),
      tokens: [] as RecipeShareToken[],
    });

    const expirationDateString = computed(() => {
      return state.expirationDate.toISOString().substring(0, 10);
    });

    whenever(
      () => props.modelValue,
      () => {
        // Set expiration date to today + 30 Days
        const today = new Date();
        state.expirationDate = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
        refreshTokens();
      },
    );

    const i18n = useI18n();
    const $auth = useMealieAuth();
    const { household } = useHouseholdSelf();
    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");

    const firstDayOfWeek = computed(() => {
      return household.value?.preferences?.firstDayOfWeek || 0;
    });

    // ============================================================
    // Token Actions

    const userApi = useUserApi();

    async function createNewToken() {
      // Convert expiration date to timestamp
      const { data } = await userApi.recipes.share.createOne({
        recipeId: props.recipeId,
        expiresAt: state.expirationDate.toISOString(),
      });

      if (data) {
        state.tokens.push(data);
      }
    }

    async function deleteToken(id: string) {
      await userApi.recipes.share.deleteOne(id);
      state.tokens = state.tokens.filter(token => token.id !== id);
    }

    async function refreshTokens() {
      const { data } = await userApi.recipes.share.getAll(1, -1, { recipe_id: props.recipeId });

      if (data) {
        // @ts-expect-error - TODO: This routes doesn't have pagination, but the type are mismatched.
        state.tokens = data ?? [];
      }
    }

    const { share, isSupported: shareIsSupported } = useShare();
    const { copy, copied, isSupported } = useClipboard();

    function getRecipeText() {
      return i18n.t("recipe.share-recipe-message", [props.name]);
    }

    function getTokenLink(token: string) {
      return `${window.location.origin}/g/${groupSlug.value}/shared/r/${token}`;
    }

    async function copyTokenLink(token: string) {
      if (isSupported.value) {
        await copy(getTokenLink(token));
        if (copied.value) {
          alert.success(i18n.t("recipe-share.recipe-link-copied-message") as string);
        }
        else {
          alert.error(i18n.t("general.clipboard-copy-failure") as string);
        }
      }
      else {
        alert.error(i18n.t("general.clipboard-not-supported") as string);
      }
    }

    async function shareRecipe(token: string) {
      if (shareIsSupported) {
        share({
          title: props.name,
          url: getTokenLink(token),
          text: getRecipeText() as string,
        });
      }
      else {
        await copyTokenLink(token);
      }
    }

    return {
      ...toRefs(state),
      expirationDateString,
      dialog,
      createNewToken,
      deleteToken,
      firstDayOfWeek,
      shareRecipe,
      copyTokenLink,
    };
  },
});
</script>
