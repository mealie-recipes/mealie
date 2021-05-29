<template>
  <div class="mt-2">
    <v-card>
      <v-card-title class="headline">
        Log
        <v-spacer></v-spacer>
        <v-text-field
          class="ml-auto shrink mb-n7"
          solo
          :label="$t('about.log-lines')"
          type="number"
          append-icon="mdi-refresh-circle"
          v-model="lines"
          @click:append="getLogText"
          suffix="lines"
          single-line
        >
        </v-text-field>
        <TheDownloadBtn :button-text="$t('about.download-log')" download-url="/api/debug/log">
          <template v-slot:default="{ downloadFile }">
            <v-btn bottom right relative fab icon color="primary" @click="downloadFile">
              <v-icon> mdi-download </v-icon>
            </v-btn>
          </template>
        </TheDownloadBtn>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <div v-for="(item, index) in splitText" :key="index" :class="getClass(item)">
          {{ item }}
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import TheDownloadBtn from "@/components/UI/Buttons/TheDownloadBtn";
import { api } from "@/api";
export default {
  components: { TheDownloadBtn },
  data() {
    return {
      lines: 200,
      text: "",
    };
  },
  mounted() {
    this.getLogText();
  },
  computed: {
    splitText() {
      return this.text.split("/n");
    },
  },
  methods: {
    async getLogText() {
      this.text = await api.meta.getLogText(this.lines);
    },
    getClass(text) {
      const isError = text.includes("ERROR:");
      if (isError) {
        return "log--error";
      }
    },
  },
};
</script>

<style scoped>
.log-text {
  background-color: #e0e0e077;
}
.log--error {
  color: #ef5350;
}
.line-number {
  color: black;
  font-weight: bold;
}
</style>