<template>
  <div>
    <v-card-title class="headline"> {{ $t('recipe.create-recipe') }} </v-card-title>
    <v-card-text>
      {{ $t('recipe.create-a-recipe-by-providing-the-name-all-recipes-must-have-unique-names') }}
      <v-form ref="domCreateByName" @submit.prevent>
        <v-text-field
          v-model="newRecipeName"
          :label="$t('recipe.recipe-name')"
          :prepend-inner-icon="$globals.icons.primary"
          validate-on-blur
          autofocus
          filled
          clearable
          class="rounded-lg mt-2"
          rounded
          :rules="[validators.required]"
          :hint="$t('recipe.new-recipe-names-must-be-unique')"
          persistent-hint
          @keyup.enter="createByName(newRecipeName)"
        ></v-text-field>
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
import { defineComponent, reactive, toRefs, ref, useContext, useRouter, computed, useRoute } from "@nuxtjs/composition-api";
import { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { VForm } from "~/types/vuetify";

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

    const newRecipeName = ref("");
    const domCreateByName = ref<VForm | null>(null);

    async function createByName(name: string) {
      if (!domCreateByName.value?.validate() || name === "") {
        return;
      }
      const { response } = await api.recipes.createOne({ name });
      // TODO createOne claims to return a Recipe, but actually the API only returns a string
      // @ts-ignore See above
      handleResponse(response, true);
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
