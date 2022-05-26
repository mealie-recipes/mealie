<template>
  <v-form>
    <div>
      <v-card-title class="headline"> Import from Zip </v-card-title>
      <v-card-text>
        Import a single recipe that was exported from another Mealie instance.
        <v-file-input
          v-model="newRecipeZip"
          accept=".zip"
          label=".zip"
          filled
          clearable
          class="rounded-lg mt-2"
          rounded
          truncate-length="100"
          hint=".zip files must have been exported from Mealie"
          persistent-hint
          prepend-icon=""
          :prepend-inner-icon="$globals.icons.zip"
        >
        </v-file-input>
      </v-card-text>
      <v-card-actions class="justify-center">
        <div style="width: 250px">
          <BaseButton :disabled="newRecipeZip === null" large rounded block :loading="loading" @click="createByZip" />
        </div>
      </v-card-actions>
    </div>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, ref, useRouter } from "@nuxtjs/composition-api";
import { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";

export default defineComponent({
  setup() {
    const state = reactive({
      error: false,
      loading: false,
    });
    const api = useUserApi();
    const router = useRouter();

    function handleResponse(response: AxiosResponse<string> | null, edit = false) {
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      router.push(`/recipe/${response.data}?edit=${edit.toString()}`);
    }

    const newRecipeZip = ref<File | null>(null);
    const newRecipeZipFileName = "archive";

    async function createByZip() {
      if (!newRecipeZip.value) {
        return;
      }
      const formData = new FormData();
      formData.append(newRecipeZipFileName, newRecipeZip.value);

      const { response } = await api.upload.file("/api/recipes/create-from-zip", formData);
      handleResponse(response);
    }

    return {
      newRecipeZip,
      createByZip,
      ...toRefs(state),
      validators,
    };
  },
});
</script>
