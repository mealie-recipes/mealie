<template>
  <BaseDialog
    v-if="currentAnnouncement"
    v-model="dialog"
    :title="$t('announcements.announcements')"
    :icon="$globals.icons.bullhornVariant"
    :cancel-text="$t('general.done')"
    width="100%"
    max-width="1200"
  >
    <div class="d-flex" :style="{ height: useMobile ? '100%' : '60vh', minHeight: '60vh' }">
      <!-- Nav list -->
      <v-list
        v-show="!useMobile || navOpen"
        nav
        density="compact"
        color="primary"
        class="overflow-y-auto border-e flex-shrink-0"
        style="width: 200px; max-height: 60vh"
      >
        <v-list-item
          v-for="announcement in allAnnouncements.toReversed()"
          :key="announcement.key"
          :active="currentAnnouncement.key === announcement.key"
          rounded
          @click="setCurrentAnnouncement(announcement); navOpen = false"
        >
          <v-list-item-title class="text-body-2">
            {{ announcement.meta?.title }}
          </v-list-item-title>
          <v-list-item-subtitle v-if="announcement.date">
            {{ $d(announcement.date) }}
          </v-list-item-subtitle>

          <template v-if="newAnnouncements.some(a => a.key === announcement.key)" #append>
            <v-icon size="x-small" color="info">
              {{ $globals.icons.alertCircle }}
            </v-icon>
          </template>
        </v-list-item>
      </v-list>

      <!-- Main content -->
      <div
        class="flex-grow-1 overflow-y-auto"
      >
        <v-btn
          v-if="useMobile"
          :prepend-icon="navOpen ? $globals.icons.chevronLeft : $globals.icons.chevronRight"
          density="compact"
          variant="text"
          class="mt-2 ms-2"
          @click="navOpen = !navOpen"
        >
          {{ $t("announcements.all-announcements") }}
        </v-btn>
        <v-card-title>
          <v-chip v-if="currentAnnouncement.date" label large class="me-1">
            <v-icon class="me-1">
              {{ $globals.icons.calendar }}
            </v-icon>
            {{ $d(currentAnnouncement.date) }}
          </v-chip>
          {{ currentAnnouncement.meta?.title }}
        </v-card-title>
        <v-card-text>
          <component :is="currentAnnouncement.component" />
        </v-card-text>
      </div>
    </div>
    <template #custom-card-action>
      <BaseButton
        v-if="newAnnouncements.length"
        color="success"
        :icon="$globals.icons.textBoxCheckOutline"
        :text="$t('announcements.mark-all-as-read')"
        @click="markAllAsRead"
      />
      <BaseButton
        :disabled="isLastAnnouncement(currentAnnouncement.key)"
        color="info"
        :icon="$globals.icons.arrowRightBold"
        icon-right
        :text="$t('general.next')"
        @click="nextAnnouncement"
      />
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { useAnnouncements } from "~/composables/use-announcements";
import type { Announcement } from "~/composables/use-announcements";

const dialog = defineModel<boolean>({ default: false });

const display = useDisplay();
const useMobile = computed(() => display.smAndDown.value);
const navOpen = ref(false);

const route = useRoute();
watch(() => route.fullPath, () => { dialog.value = false; });

const { newAnnouncements, allAnnouncements, setLastRead, markAllAsRead } = useAnnouncements();

const currentAnnouncement = shallowRef<Announcement | undefined>();

watch(dialog, () => {
  if (!dialog.value || currentAnnouncement.value) {
    return;
  }

  // Show first unread on open, or fall back to the newest
  const next = newAnnouncements.value.at(0) || allAnnouncements.at(-1)!;
  setCurrentAnnouncement(next);
});

function setCurrentAnnouncement(announcement: Announcement) {
  currentAnnouncement.value = announcement;
  setLastRead(announcement.key);
}

function nextAnnouncement() {
  // Find the first unread announcement after the current one (current is already removed from newAnnouncements)
  const next = newAnnouncements.value.find(a => a.key > currentAnnouncement.value!.key);
  if (next) {
    setCurrentAnnouncement(next);
  }
}

function isLastAnnouncement(key: string) {
  if (!newAnnouncements.value.length) {
    return true;
  }
  else {
    return key >= newAnnouncements.value.at(-1)!.key;
  }
}
</script>
