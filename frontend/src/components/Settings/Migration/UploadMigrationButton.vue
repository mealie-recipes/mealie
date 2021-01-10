<template>
  <v-form ref="file">
    <v-file-input
      :loading="loading"
      label="Upload an Archive"
      v-model="file"
      accept=".zip"
      @change="upload"
    >
    </v-file-input>
  </v-form>
</template>

<script>
import api from "../../../api";
export default {
  data() {
    return {
      file: null,
      loading: false,
    };
  },
  methods: {
    async upload() {
      if (this.file != null) {
        this.loading = true;
        let formData = new FormData();
        formData.append("archive", this.file);

        await api.migrations.uploadFile(formData);

        this.loading = false;
        this.$emit("uploaded");
        this.file = null;
      }
    },
  },
};
</script>

<style>
</style>