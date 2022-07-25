<template>
  <div>
    <v-card-title class="headline"> Create Recipe from an Image </v-card-title>
    <v-card-text>
      Create a recipe by uploading a scan.
      <v-form ref="domCreateByOcr"> </v-form>
    </v-card-text>
    <v-card-actions class="justify-center">
      <v-checkbox v-model="makeFileRecipeImage" :label="$t('new-recipe.make-recipe-image')" />
    </v-card-actions>
    <v-card-actions class="justify-center">
      <AppButtonUpload :post="false" file-name="file" :text-btn="false" @uploaded="createByOcr" accept="image/*" />
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

    function handleResponse(response: AxiosResponse<string> | null) {
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      router.push(`/recipe/${response.data}/ocr-editor`);
    }

    const domCreateByOcr = ref<VForm | null>(null);

    async function createByOcr(file: File) {
      console.log("file: ", file);
      const { response } = await api.recipes.createFromOcr(file, state.makeFileRecipeImage);
      // @ts-ignore returns a string and not a full Recipe
      handleResponse(response);
    }

    return {
      domCreateByOcr,
      createByOcr,
      ...toRefs(state),
      validators,
    };
  },
});
</script>
