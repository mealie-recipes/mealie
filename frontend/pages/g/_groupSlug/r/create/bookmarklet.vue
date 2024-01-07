<template>
    <div>
      <v-form ref="domUrlForm" @submit.prevent="createBookmarklet(importKeywordsAsTags, stayInEditMode)">
        <div>
          <v-card-title class="headline"> {{ $t('recipe.create-bookmarklet') }} </v-card-title>
          <v-card-text>
            {{ $t('recipe.create-bookmarklet-description') }}
            <v-checkbox v-model="importKeywordsAsTags" hide-details :label="$t('recipe.import-original-keywords-as-tags')" />
            <v-checkbox v-model="stayInEditMode" hide-details :label="$t('recipe.stay-in-edit-mode')" />
          </v-card-text>
          <v-card-actions class="justify-center">
            <div style="width: 250px">
              <BaseButton rounded block type="submit" :loading="loading" />
            </div>
          </v-card-actions>
        </div>
      </v-form>
      <v-expand-transition>
        <v-alert v-show="error" color="error" class="mt-6 white--text">
          <v-card-title class="ma-0 pa-0">
            <v-icon left color="white" x-large> {{ $globals.icons.robot }} </v-icon>
            {{ $t("new-recipe.error-title") }}
          </v-card-title>
          <v-divider class="my-3 mx-2"></v-divider>

          <p>
            {{ $t("new-recipe.error-details") }}
          </p>

        </v-alert>
      </v-expand-transition>
    </div>
  </template>

  <script lang="ts">
  import {
    defineComponent,
    reactive,
    toRefs,
    ref,
    useRouter,
    computed,
    useContext,
    useRoute
  } from "@nuxtjs/composition-api";
  import { AxiosResponse } from "axios";
  import { useUserApi } from "~/composables/api";
  import { useTagStore } from "~/composables/store/use-tag-store";
  import { validators } from "~/composables/use-validators";
  import { VForm } from "~/types/vuetify";

  export default defineComponent({
    setup() {
      const state = reactive({
        error: false,
        loading: false,
      });

      const { $auth } = useContext();
      const api = useUserApi();
      const route = useRoute();
      const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

      const router = useRouter();
      const tags = useTagStore();

      function handleResponse(response: AxiosResponse<string> | null, edit = false, refreshTags = false) {
        if (response?.status !== 201) {
          state.error = true;
          state.loading = false;
          return;
        }
        if (refreshTags) {
          tags.actions.refresh();
        }

      }

      const importKeywordsAsTags = computed({
        get() {
          return route.value.query.use_keywords === "1";
        },
        set(v: boolean) {
          router.replace({ query: { ...route.value.query, use_keywords: v ? "1" : "0" } });
        },
      });

      const stayInEditMode = computed({
        get() {
          return route.value.query.edit === "1";
        },
        set(v: boolean) {
          router.replace({ query: { ...route.value.query, edit: v ? "1" : "0" } });
        },
      });

      const domUrlForm = ref<VForm | null>(null);

      async function createBookmarklet(importKeywordsAsTags: boolean, stayInEditMode: boolean) {
        state.loading = true;
        const { response } = await api.recipes.createOneByUrl("https://mattmcnamara.com", importKeywordsAsTags);
        handleResponse(response, stayInEditMode, importKeywordsAsTags);
      }

      return {
        importKeywordsAsTags,
        stayInEditMode,
        domUrlForm,
        createBookmarklet,
        ...toRefs(state),
        validators,
      };
    },
  });
  </script>1

  <style>
  .force-white > a {
    color: white !important;
  }
  </style>
