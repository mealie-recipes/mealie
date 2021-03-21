<template>
  <v-form ref="file">
    <input ref="uploader" class="d-none" type="file" @change="onFileChanged" />
    <v-btn :loading="isSelecting" @click="onButtonClick" color="accent" text>
      <v-icon left> {{ icon }}</v-icon>
      {{ text ? text : defaultText }}
    </v-btn>
  </v-form>
</template>

<script>
const UPLOAD_EVENT = "uploaded";
import api from "@/api";
export default {
  props: {
    url: String,
    text: { default: "Upload" },
    icon: { default: "mdi-cloud-upload" },
    fileName: { default: "archive" },
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
        let formData = new FormData();
        formData.append(this.fileName, this.file);

        await api.utils.uploadFile(this.url, formData);

        this.isSelecting = false;
        this.$emit(UPLOAD_EVENT);
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