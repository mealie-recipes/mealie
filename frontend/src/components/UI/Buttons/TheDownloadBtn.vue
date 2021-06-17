<template>
  <div>
    <slot v-bind="{ downloading, downloadFile }">
      <v-btn color="accent" text :loading="downloading" @click="downloadFile">
        {{ showButtonText }}
      </v-btn>
    </slot>
  </div>
</template>

<script>
/**
 * The download button used for the entire site
 * pass a URL to the endpoint that will return a
 * file_token which will then be used to request the file
 * from the server and open that link in a new tab
 */
import { apiReq } from "@/api/api-utils";
export default {
  props: {
    /**
     * URL to get token from
     */
    downloadUrl: {
      default: "",
    },
    /**
     * Override button text. Defaults to "Download"
     */
    buttonText: {
      default: null,
    },
  },
  data() {
    return {
      downloading: false,
    };
  },
  computed: {
    showButtonText() {
      return this.buttonText || this.$t("general.download");
    },
  },
  methods: {
    async downloadFile() {
      this.downloading = true;
      await apiReq.download(this.downloadUrl);
      this.downloading = false;
    },
  },
};
</script>

<style lang="scss" scoped></style>
