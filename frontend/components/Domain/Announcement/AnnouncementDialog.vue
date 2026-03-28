<template>
  <BaseDialog
    v-model="dialog"
    :title="$t('announcements.announcements')"
    :icon="$globals.icons.bullhornVariant"
    width="100%"
    max-width="1200"
  >
    <v-card-title>
      <v-chip label large class="me-1">
        <v-icon class="me-1">
          {{ $globals.icons.calendar }}
        </v-icon>
        {{ $d(new Date(currentAnnouncement.key.split('_', 1)[0])) }}
      </v-chip>
      {{ currentAnnouncement.meta?.title }}
    </v-card-title>
    <v-card-text>
      <component :is="currentAnnouncement.component" />
    </v-card-text>
  </BaseDialog>
</template>

<script setup lang="ts">
import { useAnnouncements } from "~/composables/use-announcements";
import { useUserApi } from "~/composables/api";

const dialog = defineModel<boolean>({ default: false });

const auth = useMealieAuth();
const api = useUserApi();
const { newAnnouncements, allAnnouncements } = useAnnouncements();

const currentAnnouncement = shallowRef(newAnnouncements.value.at(0) || allAnnouncements.at(-1)!);
watch(
  () => dialog,
  () => {
    // Once the dialog is opened, mark the current announcement as read
    if (dialog.value) {
      setLastRead(currentAnnouncement.value.key);
    }
  },
);

async function setLastRead(key: string) {
  const user = auth.user.value!;
  if (user.lastReadAnnouncement && key < user.lastReadAnnouncement) {
    // Don't update the last read announcement if it's older than the current one
    return;
  }

  await api.users.updateOne(
    user.id,
    {
      ...user,
      lastReadAnnouncement: key,
    },
  );
}

function markAllAsRead() {
  const newestAnnouncement = allAnnouncements.at(-1)!;
  setLastRead(newestAnnouncement.key);
}

function nextAnnouncement() {
  newAnnouncements.value.shift();
  const nextAnnouncement = newAnnouncements.value.at(0);
  if (!nextAnnouncement) {
    return;
  }

  currentAnnouncement.value = nextAnnouncement;
  setLastRead(currentAnnouncement.value.key);
}
</script>
