<template>
  <div>
    <The404>
      <h1 class="mx-auto">{{ $t('general.no-recipe-found') }}</h1>
    </The404>
  </div>
</template>

<script>
import The404 from "./The404.vue";
export default {
  components: { The404 },
};
</script>



