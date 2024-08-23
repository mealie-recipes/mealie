<template>
  <div>
    <BaseDialog v-model="dialog" :title="$t('recipe-share.share-recipe')" :icon="$globals.icons.link">
      <v-card-text>
        <v-menu
          v-model="datePickerMenu"
          :close-on-content-click="false"
          transition="scale-transition"
          offset-y
          max-width="290px"
          min-width="auto"
        >
          <template #activator="{ on, attrs }">
            <v-text-field
              v-model="expirationDate"
              :label="$t('recipe-share.expiration-date')"
              :hint="$t('recipe-share.default-30-days')"
              persistent-hint
              :prepend-icon="$globals.icons.calendar"
              v-bind="attrs"
              readonly
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker
            v-model="expirationDate"
            no-title
            :first-day-of-week="firstDayOfWeek"
            :local="$i18n.locale"
            @input="datePickerMenu = false"
          />
        </v-menu>
      </v-card-text>
      <v-card-actions class="justify-end">
        <BaseButton small @click="createNewToken"> {{ $t("general.new") }}</BaseButton>
      </v-card-actions>

      <v-list-item v-for="token in tokens" :key="token.id" @click="shareRecipe(token.id)">
        <v-list-item-avatar color="grey">
          <v-icon dark class="pa-2"> {{ $globals.icons.link }} </v-icon>
        </v-list-item-avatar>

        <v-list-item-content>
          <v-list-item-title> {{ $t("recipe-share.expires-at") }} </v-list-item-title>

          <v-list-item-subtitle>{{ $d(new Date(token.expiresAt), "long") }}</v-list-item-subtitle>
        </v-list-item-content>

        <v-list-item-action>
          <v-btn icon @click.stop="deleteToken(token.id)">
            <v-icon color="error lighten-1"> {{ $globals.icons.delete }} </v-icon>
          </v-btn>
        </v-list-item-action>
        <v-list-item-action>
          <v-btn icon @click.stop="copyTokenLink(token.id)">
            <v-icon color="info lighten-1"> {{ $globals.icons.contentCopy }} </v-icon>
          </v-btn>
        </v-list-item-action>
      </v-list-item>
    </BaseDialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, toRefs, reactive, useContext, useRoute } from "@nuxtjs/composition-api";
import { useClipboard, useShare, whenever } from "@vueuse/core";
import { RecipeShareToken } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import { useHouseholdSelf } from "~/composables/use-households";
import { alert } from "~/composables/use-toast";

export default defineComponent({
  props: {
    value: {
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
  setup(props, context) {
    // V-Model Support
    const dialog = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
      },
    });

    const state = reactive({
      datePickerMenu: false,
      expirationDate: "",
      tokens: [] as RecipeShareToken[],
    });

    whenever(
      () => props.value,
      () => {
        // Set expiration date to today + 30 Days
        const today = new Date();
        const expirationDate = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
        state.expirationDate = expirationDate.toISOString().substring(0, 10);
        refreshTokens();
      }
    );

    const { $auth, i18n } = useContext();
    const { household } = useHouseholdSelf();
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

    const firstDayOfWeek = computed(() => {
      return household.value?.preferences?.firstDayOfWeek || 0;
    });

    // ============================================================
    // Token Actions

    const userApi = useUserApi();

    async function createNewToken() {
      // Convert expiration date to timestamp
      const expirationDate = new Date(state.expirationDate);

      const { data } = await userApi.recipes.share.createOne({
        recipeId: props.recipeId,
        expiresAt: expirationDate.toISOString(),
      });

      if (data) {
        state.tokens.push(data);
      }
    }

    async function deleteToken(id: string) {
      await userApi.recipes.share.deleteOne(id);
      state.tokens = state.tokens.filter((token) => token.id !== id);
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
      } else {
        await copyTokenLink(token);
      }
    }

    return {
      ...toRefs(state),
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
