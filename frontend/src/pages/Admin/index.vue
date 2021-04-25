<template>
  <div>
    <v-container>
      <v-slide-x-transition hide-on-leave>
        <router-view></router-view>
      </v-slide-x-transition>
    </v-container>
  </div>
</template>

<script>
export default {};
</script>

<style>
</style>