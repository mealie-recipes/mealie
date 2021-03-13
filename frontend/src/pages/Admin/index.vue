<template>
  <div>
    <v-container height="100%">
      <AdminSidebar />
      <v-slide-x-transition hide-on-leave>
        <router-view></router-view>
      </v-slide-x-transition>
    </v-container>
    <!-- <v-footer absolute>
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
import axios from "axios";
import api from "@/api";
export default {
  components: {
    AdminSidebar,
  },
  data() {
    return {
      latestVersion: null,
      version: null,
    };
  },
  async mounted() {
    this.getVersion();
    let versionData = await api.meta.get_version();
    this.version = versionData.version;
  },
  computed: {
    newVersion() {
      if ((this.latestVersion != null) & (this.latestVersion != this.version)) {
        return true;
      } else {
        return false;
      }
    },
  },
  methods: {
    async getVersion() {
      let response = await axios.get(
        "https://api.github.com/repos/hay-kot/mealie/releases/latest",
        {
          headers: {
            "content-type": "application/json",
            Authorization: null,
          },
        }
      );
      this.latestVersion = response.data.tag_name;
    },
  },
};
</script>

<style>
</style>