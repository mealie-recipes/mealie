<template>
  <div>
    <AdminSidebar />
    <v-slide-x-transition hide-on-leave>
      <router-view></router-view>
    </v-slide-x-transition>
  </div>
</template>

<script>
import AdminSidebar from "../../components/Admin/AdminSidebar";
export default {
  components: {
    AdminSidebar,
  },
};
</script>

<style>
</style>