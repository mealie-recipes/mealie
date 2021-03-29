<template>
  <div>
    <v-container>
      <v-slide-x-transition hide-on-leave>
        <router-view></router-view>
      </v-slide-x-transition>
      <AdminSidebar />
    </v-container>
    <!-- <v-footer relative padding>
      <div class="flex text-center" cols="12">
        {{ $t("settings.current") }}
        {{ version }} |
        {{ $t("settings.latest") }}
        {{ latestVersion }}
        ·
        <a href="https://hay-kot.github.io/mealie/" target="_blank">
          {{ $t("settings.explore-the-docs") }}
        </a>
        ·
        <a
          href="https://hay-kot.github.io/mealie/contributors/non-coders/"
          target="_blank"
        >
          {{ $t("settings.contribute") }}
        </a>
      </div>
    </v-footer> -->
  </div>
</template>

<script>
import AdminSidebar from "@/components/Admin/AdminSidebar";

export default {
  components: {
    AdminSidebar,
  },
};
</script>

<style>
</style>