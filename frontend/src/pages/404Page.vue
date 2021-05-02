<template>
  <v-container class="text-center">
    <v-row>
      <v-col cols="2"></v-col>
      <v-col>
        <v-card height="">
          <v-card-text>
            <h1>{{ $t("404.page-not-found") }}</h1>
          </v-card-text>
          <v-btn text block @click="$router.push('/')"> {{ $t("404.take-me-home") }} </v-btn>
        </v-card>
      </v-col>
      <v-col cols="2"></v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {};
</script>

<style lang="scss" scoped></style>
