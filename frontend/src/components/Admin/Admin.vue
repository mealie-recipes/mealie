<template>
  <v-container>
    <v-alert v-if="newVersion" color="green" type="success" outlined>
      A New Version of Mealie is Avaiable,
      <a href="https://github.com/hay-kot/mealie" class="green--text">
        Visit the Repo
      </a>
    </v-alert>
    <Theme />
    <Backup />
    <Webhooks />
    <Migration />
    <v-card flat dense class="my-2" height="35px">
      <v-card-text class="text-center">
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
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import Backup from "./Backup";
import Webhooks from "./Webhooks";
import Theme from "./Theme";
import Migration from "./Migration";
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
      version: "v0.0.1",
    };
  },
  mounted() {
    this.getVersion();
  },
  computed: {
    newVersion() {
      if ((this.latestVersion != null) & (this.latestVersion != this.version)) {
        console.log("New Version Avaiable");
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
      console.log(response);
      this.latestVersion = response.data.tag_name;
    },
  },
};
</script>

<style>
</style>