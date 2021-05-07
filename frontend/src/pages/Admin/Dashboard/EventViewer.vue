<template>
  <div>
    <StatCard icon="mdi-bell-ring" :color="color">
      <template v-slot:after-heading>
        <div class="ml-auto text-right">
          <h2 class="body-3 grey--text font-weight-light">
            {{$t('settings.events')}}
          </h2>

          <h3 class="display-2 font-weight-light text--primary">
            <small> {{ total }} </small>
          </h3>
        </div>
      </template>
      <div class="d-flex row py-3 justify-end">
        <v-btn class="mx-2" small :color="color" @click="deleteAll">
          <v-icon left> mdi-notification-clear-all </v-icon> {{$t('general.clear')}}
        </v-btn>
      </div>
      <template v-slot:bottom>
        <v-virtual-scroll height="290" item-height="70" :items="events">
          <template v-slot:default="{ item }">
            <v-list-item>
              <v-list-item-avatar>
                <v-icon large dark :color="icons[item.category].color">
                  {{ icons[item.category].icon }}
                </v-icon>
              </v-list-item-avatar>

              <v-list-item-content>
                <v-list-item-title v-text="item.title"></v-list-item-title>

                <v-list-item-subtitle v-text="item.text"></v-list-item-subtitle>
                <v-list-item-subtitle>
                  {{ $d(Date.parse(item.timeStamp), "long") }}
                </v-list-item-subtitle>
              </v-list-item-content>

              <v-list-item-action class="ml-auto">
                <v-btn large icon @click="deleteEvent(item.id)">
                  <v-icon color="error">mdi-delete</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </template>
        </v-virtual-scroll>
      </template>
    </StatCard>
  </div>
</template>

<script>
import { api } from "@/api";
import StatCard from "@/components/UI/StatCard";
export default {
  components: { StatCard },
  data() {
    return {
      color: "accent",
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