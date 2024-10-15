<template>
  <v-form>
    <div>
      <v-card-title class="headline"> {{ $t('recipe.import-from-zip') }} </v-card-title>
      <v-card-text>
        {{ $t('recipe.import-from-zip-description') }}
        <v-file-input
          v-model="newRecipeZip"
          accept=".zip"
          label=".zip"
          filled
          clearable
          class="rounded-lg mt-2"
          rounded
          truncate-length="100"
          :hint="$t('recipe.zip-files-must-have-been-exported-from-mealie')"
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
import { computed, defineComponent, reactive, toRefs, ref, useContext, useRoute, useRouter } from "@nuxtjs/composition-api";
import { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";

export default defineComponent({
  setup() {
    const state = reactive({
      error: false,
      loading: false,
    });
    const { $auth } = useContext();
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

    const api = useUserApi();
    const router = useRouter();

    function handleResponse(response: AxiosResponse<string> | null, edit = false) {
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      router.push(`/g/${groupSlug.value}/r/${response.data}?edit=${edit.toString()}`);
    }

    const newRecipeZip = ref<File | null>(null);
    const newRecipeZipFileName = "archive";

    async function createByZip() {
      if (!newRecipeZip.value) {
        return;
      }
      const formData = new FormData();
      formData.append(newRecipeZipFileName, newRecipeZip.value);

      const { response } = await api.upload.file("/api/recipes/create/zip", formData);
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
