<template>
  <div>
    <v-card-actions class="justify-end">
      <v-text-field
        v-if="isEditForm"
        v-model="recipe.orgURL"
        class="mt-10"
        :label="$t('recipe.original-url')"
      ></v-text-field>
      <v-btn
        v-else-if="recipe.orgURL && !isCookMode"
        dense
        small
        :hover="false"
        type="label"
        :ripple="false"
        elevation="0"
        :href="recipe.orgURL"
        color="secondary darken-1"
        target="_blank"
        class="rounded-sm mr-4"
      >
        {{ $t("recipe.original-url") }}
      </v-btn>
    </v-card-actions>
    <AdvancedOnly>
      <v-card v-if="isEditForm" flat class="ma-2 mb-2">
        <v-card-title> API Extras </v-card-title>
        <v-divider class="mx-2"></v-divider>
        <v-card-text>
          Recipes extras are a key feature of the Mealie API. They allow you to create custom json key/value pairs
          within a recipe to reference from 3rd part applications. You can use these keys to contain information to
          trigger automation or custom messages to relay to your desired device.
          <v-row v-for="(_, key) in recipe.extras" :key="key" class="mt-1">
            <v-col cols="8">
              <v-text-field v-model="recipe.extras[key]" dense :label="key">
                <template #prepend>
                  <v-btn color="error" icon class="mt-n4" @click="removeApiExtra(key)">
                    <v-icon> {{ $globals.icons.delete }} </v-icon>
                  </v-btn>
                </template>
              </v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="d-flex">
          <div style="max-width: 200px">
            <v-text-field v-model="apiNewKey" label="Message Key"></v-text-field>
          </div>
          <BaseButton create small class="ml-5" @click="createApiExtra" />
        </v-card-actions>
      </v-card>
    </AdvancedOnly>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { usePageState } from "~/composables/recipe-page/shared-state";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
export default defineComponent({
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const { isEditForm, isCookMode } = usePageState(props.recipe.slug);
    const apiNewKey = ref("");

    function createApiExtra() {
      if (!props.recipe) {
        return;
      }

      if (!props.recipe.extras) {
        props.recipe.extras = {};
      }

      // check for duplicate keys
      if (Object.keys(props.recipe.extras).includes(apiNewKey.value)) {
        return;
      }

      props.recipe.extras[apiNewKey.value] = "";

      apiNewKey.value = "";
    }

    function removeApiExtra(key: string | number) {
      if (!props.recipe) {
        return;
      }

      if (!props.recipe.extras) {
        return;
      }

      delete props.recipe.extras[key];
      props.recipe.extras = { ...props.recipe.extras };
    }
    return {
      removeApiExtra,
      createApiExtra,
      apiNewKey,
      isEditForm,
      isCookMode,
    };
  },
});
</script>
