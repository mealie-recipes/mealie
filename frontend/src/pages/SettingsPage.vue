<template>
  <v-container>
    <v-alert v-if="newVersion" color="green" type="success" outlined>
      A New Version of Mealie is Avaiable,
      <a
        href="https://github.com/hay-kot/mealie/releases/latest"
        target="_blank"
        class="green--text"
      >
        Visit the Repo
      </a>
    </v-alert>
    <Theme />
    <Backup class="mt-2" />
    <Webhooks class="mt-2" />
    <Migration class="mt-2" />
    <p class="text-center my-2">
      Version: {{ version }} | Latest: {{ latestVersion }} ·
      <a href="https://hay-kot.github.io/mealie/" target="_blank">
        Explore the Docs
      </a>
      ·
      <a
        href="https://hay-kot.github.io/mealie/2.1%20-%20Contributions/"
        target="_blank"
      >
        Contribute
      </a>
    </p>
  </v-container>
</template>

<script>
import Backup from "../components/Settings/Backup";
import Webhooks from "../components/Settings/Webhook";
import Theme from "../components/Settings/Theme";
import Migration from "../components/Settings/Migration";
import axios from "axios";

export default {
  components: {
    Backup,
    Webhooks,
    Theme,
    Migration,
  },
  data() {
    return {
      latestVersion: null,
      version: "v0.0.2",
    };
  },
  mounted() {
    this.getVersion();
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
        "https://api.github.com/repos/hay-kot/mealie/releases/latest"
      );
      this.latestVersion = response.data.tag_name;
    },
  },
};
</script>

<style>
</style>