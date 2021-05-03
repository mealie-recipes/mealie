<template>
  <div>
    <StatCard icon="mdi-bell-ring">
      <template v-slot:after-heading>
        <div class="ml-auto text-right">
          <div class="body-3 grey--text font-weight-light" v-text="'Events'" />

          <h3 class="display-2 font-weight-light text--primary">
            <small> {{ total }}</small>
          </h3>
        </div>
      </template>
      <div class="d-flex row py-3 justify-end">
        <v-btn class="mx-2" small color="primary" @click="deleteAll">
          <v-icon left> mdi-notification-clear-all </v-icon> Clear
        </v-btn>
      </div>
      <template v-slot:bottom>
        <v-list subheader two-line>
          <v-list-item v-for="(event, index) in events" :key="index">
            <v-list-item-avatar>
              <v-icon large dark :color="icons[event.category].color">
                {{ icons[event.category].icon }}
              </v-icon>
            </v-list-item-avatar>

            <v-list-item-content>
              <v-list-item-title v-text="event.title"></v-list-item-title>

              <v-list-item-subtitle v-text="event.text"></v-list-item-subtitle>
              <v-list-item-subtitle>
                {{ $d(Date.parse(event.timeStamp), "long") }}
              </v-list-item-subtitle>
            </v-list-item-content>

            <v-list-item-action class="ml-auto">
              <v-btn large icon @click="deleteEvent(event.id)">
                <v-icon color="error">mdi-delete</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </template>
    </StatCard>
  </div>
</template>

<script>
import { api } from "@/api";
import StatCard from "./StatCard";
export default {
  components: { StatCard },
  data() {
    return {
      total: 0,
      events: [],
      icons: {
        general: {
          icon: "mdi-information",
          color: "info",
        },
        recipe: {
          icon: "mdi-silverware-fork-knife",
          color: "primary",
        },
        backup: {
          icon: "mdi-backup-restore",
          color: "primary",
        },
        schedule: {
          icon: "mdi-calendar-clock",
          color: "primary",
        },
        migration: {
          icon: "mdi-database-import",
          color: "primary",
        },
        signup: {
          icon: "mdi-account",
          color: "primary",
        },
      },
    };
  },
  mounted() {
    this.getEvents();
  },
  methods: {
    async getEvents() {
      const events = await api.about.getEvents();
      this.events = events.events;
      this.total = events.total;
    },
    async deleteEvent(id) {
      await api.about.deleteEvent(id);
      this.getEvents();
    },
    async deleteAll() {
      await api.about.deleteAllEvents();
      this.getEvents();
    },
  },
};
</script>

<style lang="scss" scoped>
</style>