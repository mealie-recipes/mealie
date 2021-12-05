<template>
  <div>
    <BaseDialog v-model="dialog" title="Share Recipe" :icon="$globals.icons.link">
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
              label="Expiration Date"
              hint="Default 30 Days"
              persistent-hint
              :prepend-icon="$globals.icons.calendar"
              v-bind="attrs"
              readonly
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker v-model="expirationDate" no-title @input="pickerMenu = false"></v-date-picker>
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
          <v-list-item-title> Expires At </v-list-item-title>

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
import { defineComponent, computed, toRefs, reactive, useContext } from "@nuxtjs/composition-api";
import { whenever } from "@vueuse/shared";
import { useClipboard, useShare } from "@vueuse/core";
import { RecipeShareToken } from "~/api/class-interfaces/recipes/recipe-share";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";

export default defineComponent({
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    recipeId: {
      type: Number,
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
        console.log(val);
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

    // ============================================================
    // Token Actions

    const userApi = useUserApi();

    async function createNewToken() {
      // Convert expiration date to timestamp
      const expirationDate = new Date(state.expirationDate);

      const { data } = await userApi.recipes.share.createOne({
        recipeId: props.recipeId,
        expiresAt: expirationDate,
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
      const { data } = await userApi.recipes.share.getAll(0, 999, { recipe_id: props.recipeId });

      if (data) {
        state.tokens = data;
      }
    }

    const { i18n } = useContext();
    const { share, isSupported: shareIsSupported } = useShare();
    const { copy } = useClipboard();

    function getRecipeText() {
      return i18n.t("recipe.share-recipe-message", [props.name]);
    }

    function getTokenLink(token: string) {
      return `${window.location.origin}/shared/recipes/${token}`;
    }

    async function copyTokenLink(token: string) {
      await copy(getTokenLink(token));
      alert.success("Recipe link copied to clipboard");
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
      shareRecipe,
      copyTokenLink,
    };
  },
});
</script>