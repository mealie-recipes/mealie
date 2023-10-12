<template>
  <CookbookPage />
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import CookbookPage from "@/components/Domain/Cookbook/CookbookPage.vue";

export default defineComponent({
  components: { CookbookPage },
})
</script>
