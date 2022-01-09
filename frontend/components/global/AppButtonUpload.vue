<template>
  <v-form ref="file">
    <input ref="uploader" class="d-none" type="file" :accept="accept" @change="onFileChanged" />
    <slot v-bind="{ isSelecting, onButtonClick }">
      <v-btn :loading="isSelecting" :small="small" color="info" :text="textBtn" @click="onButtonClick">
        <v-icon left> {{ effIcon }}</v-icon>
        {{ text ? text : defaultText }}
      </v-btn>
    </slot>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";

const UPLOAD_EVENT = "uploaded";

export default defineComponent({
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
    accept: {
      type: String,
      default: "",
    },
  },
  setup(props, context) {
    const file = ref<File | null>(null);
    const uploader = ref<HTMLInputElement | null>(null);
    const isSelecting = ref(false);

    const { i18n, $globals } = useContext();
    const effIcon = props.icon ? props.icon : $globals.icons.upload;

    const defaultText = i18n.t("general.upload");

    const api = useUserApi();
    async function upload() {
      if (file.value != null) {
        isSelecting.value = true;

        if (!props.post) {
          context.emit(UPLOAD_EVENT, file.value);
          isSelecting.value = false;
          return;
        }

        const formData = new FormData();
        formData.append(props.fileName, file.value);

        const response = await api.upload.file(props.url, formData);

        if (response) {
          context.emit(UPLOAD_EVENT, response);
        }
        isSelecting.value = false;
      }
    }

    function onFileChanged(e: Event) {
      const target = e.target as HTMLInputElement;
      if (target.files !== null && target.files.length > 0 && file.value !== null) {
        file.value = target.files[0];
        upload();
      }
    }

    function onButtonClick() {
      isSelecting.value = true;
      window.addEventListener(
        "focus",
        () => {
          isSelecting.value = false;
        },
        { once: true }
      );
      uploader.value?.click();
    }

    return {
      file,
      uploader,
      isSelecting,
      effIcon,
      defaultText,
      onFileChanged,
      onButtonClick,
    };
  },
});
</script>

<style></style>
