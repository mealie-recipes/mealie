<template>
  <v-form ref="file">
    <v-file-input
      :loading="loading"
      label="Upload an Archive"
      v-model="file"
      accept=".zip"
      @change="upload"
      :prepend-icon="icon"
      class="file-icon"
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
      icon: "mdi-paperclip",
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
        this.icon = "mdi-check";
      }
    },
  },
};
</script>

<style>
.file-icon {
  transition-duration: 5s;
}
</style>