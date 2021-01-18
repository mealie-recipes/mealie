<template>
  <v-form ref="file">
    <v-file-input
      :loading="loading"
      :label="$t('migration.upload-an-archive')"
      v-model="file"
      accept=".zip"
      @change="upload"
      :prepend-icon="icon"
      class="file-icon"
    >
    </v-file-input>
    <v-btn color="success" text class="ma-2 white--text">
      Upload
      <v-icon right dark> mdi-cloud-upload </v-icon>
    </v-btn>
  </v-form>
</template>

<script>
export default {};
</script>

<style>
</style>