<template>
  <div>
    <v-card-title class="headline">
      {{ $t('recipe.create-recipe') }}
    </v-card-title>
    <v-card-text>
      {{ $t('recipe.create-a-recipe-by-providing-the-name-all-recipes-must-have-unique-names') }}
      <v-form
        ref="domCreateByName"
        @submit.prevent
      >
        <v-text-field
          v-model="newRecipeName"
          :label="$t('recipe.recipe-name')"
          :prepend-inner-icon="$globals.icons.primary"
          validate-on="blur"
          autofocus
          variant="solo-filled"
          clearable
          class="rounded-lg mt-2"
          color="primary"
          rounded
          :rules="[validators.required]"
          :hint="$t('recipe.new-recipe-names-must-be-unique')"
          persistent-hint
          @keyup.enter="createByName(newRecipeName)"
        />
      </v-form>
    </v-card-text>
    <v-card-actions class="justify-center">
      <div style="width: 250px">
        <BaseButton
          :disabled="newRecipeName.trim() === ''"
          rounded
          block
          :loading="loading"
          @click="createByName(newRecipeName)"
        />
      </div>
    </v-card-actions>
  </div>
</template>

<script lang="ts">
import type { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import type { VForm } from "~/types/auto-forms";

export default defineNuxtComponent({
  setup() {
    const state = reactive({
      error: false,
      loading: false,
    });
    const $auth = useMealieAuth();
    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");

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

    const newRecipeName = ref("");
    const domCreateByName = ref<VForm | null>(null);

    async function createByName(name: string) {
      if (!domCreateByName.value?.validate() || name === "") {
        return;
      }
      const { response } = await api.recipes.createOne({ name });
      handleResponse(response as any, true);
    }
    return {
      domCreateByName,
      newRecipeName,
      createByName,
      ...toRefs(state),
      validators,
    };
  },
});
</script>
