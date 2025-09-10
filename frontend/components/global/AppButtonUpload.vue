<template>
  <v-form ref="files">
    <input
      ref="uploader"
      class="d-none"
      type="file"
      :accept="accept"
      :multiple="multiple"
      @change="onFileChanged"
    >
    <slot v-bind="{ isSelecting, onButtonClick }">
      <v-btn
        :loading="isSelecting"
        :small="small"
        :color="color"
        :variant="textBtn ? 'text' : 'elevated'"
        :disabled="disabled"
        @click="onButtonClick"
      >
        <v-icon start>
          {{ effIcon }}
        </v-icon>
        {{ text ? text : defaultText }}
      </v-btn>
    </slot>
  </v-form>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";

const UPLOAD_EVENT = "uploaded";

export default defineNuxtComponent({
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
    color: {
      type: String,
      default: "info",
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    multiple: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, context) {
    const files = ref<File[]>([]);
    const uploader = ref<HTMLInputElement | null>(null);
    const isSelecting = ref(false);

    const i18n = useI18n();
    const { $globals } = useNuxtApp();
    const effIcon = props.icon ? props.icon : $globals.icons.upload;

    const defaultText = i18n.t("general.upload");

    const api = useUserApi();
    async function upload() {
      if (files.value.length === 0) {
        return;
      }

      isSelecting.value = true;

      if (!props.post) {
        // NOTE: To preserve behaviour for other parents of this component,
        // we emit a single File if !props.multiple.
        context.emit(UPLOAD_EVENT, props.multiple ? files.value : files.value[0]);
        isSelecting.value = false;
        return;
      }

      // WARN: My change is only for !props.post.
      // I have not added support for multiple files in the API.
      // Existing call-sites never passed the `multiple` prop,
      // so this case will only be hit if the prop is set to true.
      if (props.multiple && files.value.length > 1) {
        console.warn("Multiple file uploads are not supported by the API.");
        return;
      }

      const file = files.value[0];
      const formData = new FormData();
      formData.append(props.fileName, file);

      try {
        const response = await api.upload.file(props.url, formData);
        if (response) {
          context.emit(UPLOAD_EVENT, response);
        }
      }
      catch (e) {
        console.error(e);
        context.emit(UPLOAD_EVENT, null);
      }

      isSelecting.value = false;
    }

    function onFileChanged(e: Event) {
      const target = e.target as HTMLInputElement;

      if (target.files !== null && target.files.length > 0) {
        files.value = Array.from(target.files);
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
        { once: true },
      );
      uploader.value?.click();
    }

    return {
      files,
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
