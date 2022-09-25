<template>
  <div>
    <v-card-title class="headline"> Create Recipe from an Image </v-card-title>
    <v-card-text>
      Create a recipe by uploading a scan.
      <v-form ref="domCreateByOcr"> </v-form>
    </v-card-text>
    <v-card-actions class="justify-center">
      <v-file-input
        v-model="imageUpload"
        accept=".png"
        label="recipe.png"
        filled
        clearable
        class="rounded-lg mt-2"
        rounded
        truncate-length="100"
        hint="Upload a png image from a recipe book"
        persistent-hint
        prepend-icon=""
        :prepend-inner-icon="$globals.icons.fileImage"
      />
    </v-card-actions>
    <v-card-actions class="justify-center">
      <v-checkbox v-model="makeFileRecipeImage" :label="$t('new-recipe.make-recipe-image')" />
    </v-card-actions>
    <v-card-actions class="justify-center">
      <div style="width: 250px">
        <BaseButton :disabled="imageUpload === null" large rounded block :loading="loading" @click="createByOcr" />
      </div>
    </v-card-actions>
  </div>
</template>
<script lang="ts">
import { defineComponent, reactive, toRefs, ref, useRouter } from "@nuxtjs/composition-api";
import { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { VForm } from "~/types/vuetify";

export default defineComponent({
  setup() {
    const state = reactive({
      error: false,
      loading: false,
      makeFileRecipeImage: false,
    });
    const api = useUserApi();
    const router = useRouter();

    const imageUpload = ref<File | null>(null);

    function handleResponse(response: AxiosResponse<string> | null) {
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      router.push(`/recipe/${response.data}/ocr-editor`);
    }

    const domCreateByOcr = ref<VForm | null>(null);

    async function createByOcr() {
      if (imageUpload.value === null) return; // Should never be true due to circumstances
      state.loading = true;
      const { response } = await api.recipes.createFromOcr(imageUpload.value, state.makeFileRecipeImage);
      // @ts-ignore returns a string and not a full Recipe
      handleResponse(response);
    }

    return {
      domCreateByOcr,
      createByOcr,
      ...toRefs(state),
      validators,
      imageUpload,
    };
  },
});
</script>
