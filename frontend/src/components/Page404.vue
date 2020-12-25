<template>
  <div class="text-center">
    <v-row>
      <v-col cols="2"></v-col>
      <v-col>
        <v-card height="">
          <v-card-text>
            <h1>404 No Page Found</h1>
          </v-card-text>
          <v-btn text block @click="$router.push('/')"> Take me Home </v-btn>
        </v-card>
      </v-col>
      <v-col cols="2"></v-col>
    </v-row>
  </div>
</template>

<script>
export default {};
</script>

<style lang="scss" scoped>
</style>