<template>
  <v-form ref="file">
    <input ref="uploader" class="d-none" type="file" @change="onFileChanged" />
    <v-btn :loading="isSelecting" @click="onButtonClick" color="accent" text>
      <v-icon left> mdi-cloud-upload </v-icon>
      {{ $t('general.upload') }}
    </v-btn>
  </v-form>
</template>

<script>
import api from "../../api";
export default {
  props: {
    url: String,
  },
  data: () => ({
    defaultButtonText: this.$t("general.upload"),
    file: null,
    isSelecting: false,
  }),

  methods: {
    async upload() {
      if (this.file != null) {
        this.isSelecting = true;
        let formData = new FormData();
        formData.append("archive", this.file);

        await api.utils.uploadFile(this.url, formData);

        this.isSelecting = false;
        this.$emit("uploaded");
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