<template>
  <div>
    <ConfirmationDialog
      :title="$t('events.delete-event')"
      :message="$t('general.confirm-delete-generic')"
      color="error"
      :icon="$globals.icons.alertCircle"
      ref="deleteEventConfirm"
      v-on:confirm="emitDelete()"
    />
    <StatCard :icon="$globals.icons.bellAlert" :color="color">
      <template v-slot:after-heading>
        <div class="ml-auto text-right">
          <h2 class="body-3 grey--text font-weight-light">
            {{ $t("settings.events") }}
          </h2>

          <h3 class="display-2 font-weight-light text--primary">
            <small> {{ total }} </small>
          </h3>
        </div>
      </template>
      <div class="d-flex row py-3 justify-end">
        <v-btn class="mx-2" small color="error lighten-1" @click="deleteAll">
          <v-icon left> {{ $globals.icons.notificationClearAll }} </v-icon> {{ $t("general.clear") }}
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
                <v-btn large icon @click="openDialog(item)">
                  <v-icon color="error">{{ $globals.icons.delete }}</v-icon>
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
import ConfirmationDialog from "@/components/UI/Dialogs/ConfirmationDialog";
export default {
  components: { StatCard, ConfirmationDialog },
  data() {
    return {
      color: "accent",
      total: 0,
      selectedId: "",
      events: [],
      icons: {
        general: {
          icon: this.$globals.icons.information,
          color: "info",
        },
        recipe: {
          icon: this.$globals.icons.primary,
          color: "primary",
        },
        backup: {
          icon: this.$globals.icons.database,
          color: "primary",
        },
        schedule: {
          icon: this.$globals.icons.calendar,
          color: "primary",
        },
        migration: {
          icon: this.$globals.icons.backupRestore,
          color: "primary",
        },
        user: {
          icon: this.$globals.icons.user,
          color: "accent",
        },
        group: {
          icon: this.$globals.icons.group,
          color: "accent",
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

    openDialog(events) {
      this.selectedId = events.id;
      this.$refs.deleteEventConfirm.open();
    },

    emitDelete() {
      this.deleteEvent(this.selectedId);
    },
  },
};
</script>

<style lang="scss" scoped>
</style>