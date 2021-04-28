<template>
  <v-form ref="file">
    <input ref="uploader" class="d-none" type="file" @change="onFileChanged" />
    <v-btn
      :loading="isSelecting"
      @click="onButtonClick"
      color="accent"
      :text="textBtn"
    >
      <v-icon left> {{ icon }}</v-icon>
      {{ text ? text : defaultText }}
    </v-btn>
  </v-form>
</template>

<script>
const UPLOAD_EVENT = "uploaded";
import { api } from "@/api";
export default {
  props: {
    post: {
      type: Boolean,
      default: true,
    },
    url: String,
    text: String,
    icon: { default: "mdi-cloud-upload" },
    fileName: { default: "archive" },
    textBtn: {
      default: true,
    },
  },
  data: () => ({
    file: null,
    isSelecting: false,
  }),

  computed: {
    defaultText() {
      return this.$t("general.upload");
    },
  },

  methods: {
    async upload() {
      if (this.file != null) {
        this.isSelecting = true;

        if (!this.post) {
          this.$emit(UPLOAD_EVENT, this.file);
          this.isSelecting = false;
          return;
        }

        let formData = new FormData();
        formData.append(this.fileName, this.file);

        if(await api.utils.uploadFile(this.url, formData)) {
          this.$emit(UPLOAD_EVENT);
        }
        this.isSelecting = false;
      }
    },
    onButtonClick() {
      this.isSelecting = true;
      window.addEventListener(
        "focus",
        () => {
          this.isSelecting = false;
        },
        { once: true }
      );

      this.$refs.uploader.click();
    },
    onFileChanged(e) {
      this.file = e.target.files[0];
      this.upload();
    },
  },
};
</script>

<style>
</style>