<template>
    <v-date-picker
        :first-day-of-week="firstDayOfWeek"
        v-on="$listeners"
    ></v-date-picker>
</template>

<script>
import { api } from "@/api";

export default {
  data() {
    return {
       firstDayOfWeek: 0,
    };
  },
  mounted() {
    this.getOptions();
  },

  methods: {
    async getOptions() {
      this.firstDayOfWeek = await api.siteSettings.get().firstDayOfWeek;
    },
  },
}
</script>

<style>
</style>