<template>
  <div class="text-center">
    <v-menu v-model="menu" offset-y top nudge-top="6" :close-on-content-click="false">
      <template #activator="{ on, attrs }">
        <v-btn color="accent" dark v-bind="attrs" v-on="on">
          <v-icon left>
            {{ $globals.icons.fileImage }}
          </v-icon>
          {{ $t("general.image") }}
        </v-btn>
      </template>
      <v-card width="400">
        <v-card-title class="headline flex mb-0">
          <div>
            {{ $t("recipe.recipe-image") }}
          </div>
          <AppButtonUpload
            class="ml-auto"
            url="none"
            file-name="image"
            :text-btn="false"
            :post="false"
            @uploaded="uploadImage"
          />
        </v-card-title>
        <v-card-text class="mt-n5">
          <div>
            <v-text-field v-model="url" :label="$t('general.url')" class="pt-5" clearable :messages="messages">
              <template #append-outer>
                <v-btn class="ml-2" color="primary" :loading="loading" :disabled="!slug" @click="getImageFromURL">
                  {{ $t("general.get") }}
                </v-btn>
              </template>
            </v-text-field>
          </div>
        </v-card-text>
      </v-card>
    </v-menu>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, useContext } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";

const REFRESH_EVENT = "refresh";
const UPLOAD_EVENT = "upload";

export default defineComponent({
  props: {
    slug: {
      type: String,
      required: true,
    },
  },
  setup(props, context) {
    const state = reactive({
      url: "",
      loading: false,
      menu: false,
    })

    function uploadImage(fileObject: File) {
      context.emit(UPLOAD_EVENT, fileObject);
      state.menu = false;
    }

    const api = useUserApi();
    async function getImageFromURL() {
      state.loading = true;
      if (await api.recipes.updateImagebyURL(props.slug, state.url)) {
        context.emit(REFRESH_EVENT);
      }
      state.loading = false;
      state.menu = false;
    }

    const { i18n } = useContext();
    const messages = props.slug ? [""] : [i18n.t("recipe.save-recipe-before-use")];

    return {
      ...toRefs(state),
      uploadImage,
      getImageFromURL,
      messages,
    };
  },
});
</script>

<style lang="scss" scoped></style>
