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
    <template #custom-card-action>
      <div v-if="newAnnouncements.length">
        <BaseButton
          color="success"
          :icon="$globals.icons.textBoxCheckOutline"
          :text="$t('announcements.mark-all-as-read')"
          class="mx-4"
          @click="markAllAsRead"
        />
        <BaseButton
          color="info"
          :icon="$globals.icons.arrowRightBold"
          icon-right
          :text="$t('general.next')"
          @click="nextAnnouncement"
        />
      </div>
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { useAnnouncements } from "~/composables/use-announcements";
import { useUserApi } from "~/composables/api";

const dialog = defineModel<boolean>({ default: false });

const auth = useMealieAuth();
const api = useUserApi();
const { newAnnouncements, allAnnouncements } = useAnnouncements();

const currentAnnouncement = shallowRef<Announcement | undefined>();
watch(
  dialog,
  () => {
    // Once the dialog is opened, show the next announcement
    if (dialog.value) {
      nextAnnouncement();

      // If there are no new announcements, this is never set, so show the newest one
      if (!currentAnnouncement.value) {
        currentAnnouncement.value = allAnnouncements.at(-1);
      }
    }
  },
);

async function setLastRead(key: string) {
  const user = auth.user.value!;
  if (user.lastReadAnnouncement && key <= user.lastReadAnnouncement) {
    // Don't update the last read announcement if it's older than the current one
    return;
  }

  await api.users.updateOne(
    user.id,
    {
      ...user,
      lastReadAnnouncement: null, // TODO: switch back to key
    },
    { suppressAlert: true },
  );
}

function markAllAsRead() {
  newAnnouncements.value = [];

  const newestAnnouncement = allAnnouncements.at(-1)!;
  setLastRead(newestAnnouncement.key);
}

function nextAnnouncement() {
  const nextAnnouncement = newAnnouncements.value.at(0);
  newAnnouncements.value = newAnnouncements.value.slice(1);

  if (!nextAnnouncement) {
    markAllAsRead();
    return;
  }

  currentAnnouncement.value = nextAnnouncement;
  setLastRead(currentAnnouncement.value.key);
}
</script>
