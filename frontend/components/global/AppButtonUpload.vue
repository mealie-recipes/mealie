<template>
  <v-form ref="file">
    <input ref="uploader" class="d-none" type="file" @change="onFileChanged" />
    <slot v-bind="{ isSelecting, onButtonClick }">
      <v-btn :loading="isSelecting" :small="small" color="accent" :text="textBtn" @click="onButtonClick">
        <v-icon left> {{ effIcon }}</v-icon>
        {{ text ? text : defaultText }}
      </v-btn>
    </slot>
  </v-form>
</template>

<script>
import { useApiSingleton } from "~/composables/use-api";
const UPLOAD_EVENT = "uploaded";
export default {
  props: {
    small: {
      type: Boolean,
      default: false,
    },
    post: {
      type: Boolean,
      default: true,
    },
    url: {
      type: String,
      default: "",
    },
    text: {
      type: String,
      default: "",
    },
    icon: {
      type: String,
      default: null,
    },
    fileName: {
      type: String,
      default: "archive",
    },
    textBtn: {
      type: Boolean,
      default: true,
    },
  },
  setup() {
    const api = useApiSingleton();

    return { api };
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

        const formData = new FormData();
        formData.append(this.fileName, this.file);

        const response = await this.api.upload.file(this.url, formData);

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
