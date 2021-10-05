<template>
  <v-container fluid>
    <BaseCardSectionTitle title="Data Migrations">
      Lorem, ipsum dolor sit amet consectetur adipisicing elit. Alias error provident, eveniet, laboriosam assumenda
      earum amet quaerat vel consequatur molestias sed enim. Adipisci a consequuntur dolor culpa expedita voluptatem
      praesentium optio iste atque, ea reiciendis iure non aut suscipit modi ducimus ratione, quam numquam quaerat
      distinctio illum nemo. Dicta, doloremque!
    </BaseCardSectionTitle>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  layout: "admin",
  setup() {
    return {};
  },
  head() {
    return {
      title: this.$t("settings.migrations") as string,
    };
  },
});
</script>
    
<style scoped>
</style>