// TODO: Fix date/time Localization

<template>
  <div>
    <!-- <BaseDialog
      ref="deleteEventConfirm"
      :title="$t('events.delete-event')"
      :message="$t('general.confirm-delete-generic')"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="emitDelete()"
    /> -->
    <BaseStatCard :icon="$globals.icons.bellAlert" :color="color">
      <template #after-heading>
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
        <v-btn class="mx-2" small color="error lighten-1" @click="$emit('delete-all')">
          <v-icon left> {{ $globals.icons.notificationClearAll }} </v-icon> {{ $t("general.clear") }}
        </v-btn>
      </div>
      <template #bottom>
        <v-virtual-scroll height="290" item-height="70" :items="events">
          <template #default="{ item }">
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
                <v-btn large icon @click="$emit('delete-item', item.id)">
                  <v-icon color="error">{{ $globals.icons.delete }}</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </template>
        </v-virtual-scroll>
      </template>
    </BaseStatCard>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  layout: "admin",
  props: {
    events: {
      type: Array,
      required: true,
    },
    total: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {
      color: "accent",
      selectedId: "",
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
});
</script>

<style scoped>
</style>