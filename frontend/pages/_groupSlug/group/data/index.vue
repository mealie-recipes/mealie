<template>
  <div></div>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, useRoute, useRouter } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    value: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug);

    const router = useRouter();
    onMounted(() => {
      // Force redirect to first valid page
      router.push(`/${groupSlug.value}/group/data/foods`);
    });
    return {};
  },
});
</script>
