<template>
    <div>
      <v-form ref="domUrlForm">
        <div>
          <v-card-title class="headline"> {{ $t('recipe.create-bookmarklet') }} </v-card-title>
          <v-card-text>
            {{ $t('recipe.create-bookmarklet-description') }}
            <v-checkbox v-model="importKeywordsAsTags" validate-on-blur hide-details :label="$t('recipe.import-original-keywords-as-tags')" />
            <v-checkbox v-model="stayInEditMode" validate-on-blur hide-details :label="$t('recipe.stay-in-edit-mode')" />
          </v-card-text>
            <v-textarea
            v-model="bookmarkletResult"
            :label="$t('recipe.create-bookmarklet-result')"
            :prepend-inner-icon="$globals.icons.tags"
            filled
            rows="2"
            class="rounded-lg mt-2"
            rounded
            :hint="$t('recipe.create-bookmarklet-hint')"
            persistent-hint
            :readonly="true"
            @click="copyBookmarklet"
          ></v-textarea>

        </div>
      </v-form>
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
  import { detectServerBaseUrl } from "~/composables/use-utils";
  import { VForm } from "~/types/vuetify";
  import { useCopy } from "~/composables/use-copy";

  export default defineComponent({
    setup() {
      const { $auth, req, i18n } = useContext();

      const { copyText } = useCopy();

      const route = useRoute();

      const router = useRouter();

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

      const baseUrl = computed(() => detectServerBaseUrl(req));
      const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");
      const importKeywordsAsTagAsNumber = computed(() => Number(importKeywordsAsTags.value));
      const stayInEditModeAsNumber = computed(() => Number(stayInEditMode.value));

      const bookmarkletResult = computed({
        get() {
        const route = useRoute();

        let url = document.URL;
        let slashCount = 0;
        let position = -1;

        // The third slash is after the port portion of the URL
        while(slashCount < 3) {
          position = url.indexOf("/", position + 1);
          if (position === -1) {
            break;
          }
          slashCount++;
        }

        // Now that we found the third slash, remove it and everything after
        url = url.substring(0, position);

        // window.history.replaceState is appended to fix Vivaldi bug
        // https://forum.vivaldi.net/topic/31409/bookmarklets-replaces-the-url-in-the-address-bar/25?lang=en-US&page=2
        return encodeURIComponent(`javascript:(function(){var dest="${url}/g/${groupSlug.value}/r/create/url?use_keywords=${importKeywordsAsTagAsNumber.value}&edit=${stayInEditModeAsNumber.value}&recipe_import_url="+encodeURIComponent(document.URL);window.open(dest,"_blank");window.history.replaceState({},"",location.href);})();`);
      }
      });

      const copyBookmarklet = () => {
        copyText(bookmarkletResult.value);
      };

      return {
        importKeywordsAsTags,
        stayInEditMode,
        baseUrl,
        groupSlug,
        bookmarkletResult,
        copyBookmarklet,
        copyText,
      };
    },
  });
  </script>
