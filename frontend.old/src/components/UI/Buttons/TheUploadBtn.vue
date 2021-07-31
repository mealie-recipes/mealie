<template>
  <v-form ref="file">
    <input ref="uploader" class="d-none" type="file" @change="onFileChanged" />
    <slot v-bind="{ isSelecting, onButtonClick }">
      <v-btn :loading="isSelecting" @click="onButtonClick" :small="small" color="accent" :text="textBtn">
        <v-icon left> {{ effIcon }}</v-icon>
        {{ text ? text : defaultText }}
      </v-btn>
    </slot>
  </v-form>
</template>

<script>
const UPLOAD_EVENT = "uploaded";
import { api } from "@/api";
export default {
  props: {
    small: {
      default: false,
    },
    post: {
      type: Boolean,
      default: true,
    },
    url: String,
    text: String,
    icon: { default: null },
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
    effIcon() {
      return this.icon ? this.icon : this.$globals.icons.upload;
    },
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

        const response = await api.utils.uploadFile(this.url, formData);

        if (response) {
          this.$emit(UPLOAD_EVENT, response);
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

<style></style>
