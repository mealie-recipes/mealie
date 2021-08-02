<template>
  <div class="text-center">
    <v-menu offset-y top nudge-top="6" :close-on-content-click="false">
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
          <TheUploadBtn
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
            <v-text-field v-model="url" :label="$t('general.url')" class="pt-5" clearable :messages="getMessages()">
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

<script>
import TheUploadBtn from "@/components/UI/Buttons/TheUploadBtn";
import { api } from "@/api";
const REFRESH_EVENT = "refresh";
const UPLOAD_EVENT = "upload";
export default {
  components: {
    TheUploadBtn,
  },
  props: {
    slug: String,
  },
  data: () => ({
    url: "",
    loading: false,
  }),
  methods: {
    uploadImage(fileObject) {
      this.$emit(UPLOAD_EVENT, fileObject);
    },
    async getImageFromURL() {
      this.loading = true;
      if (await api.recipes.updateImagebyURL(this.slug, this.url)) {
        this.$emit(REFRESH_EVENT);
      }
      this.loading = false;
    },
    getMessages() {
      return this.slug ? [""] : [this.$i18n.t("recipe.save-recipe-before-use")];
    },
  },
};
</script>

<style lang="scss" scoped></style>
