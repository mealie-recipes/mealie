import { useHouseholdSelf } from "~/composables/use-households";
import { useGroupSelf } from "~/composables/use-groups";
import { useUserApi } from "~/composables/api";

export type AnnouncementMeta = {
  title: string | undefined;
};

export type Announcement = {
  key: string;
  component: Component;
  date: Date | undefined;
  meta: AnnouncementMeta | undefined;
};

const _announcementsUnsorted = import.meta.glob<{ default: Component; meta?: AnnouncementMeta }>(
  "~/components/Domain/Announcement/Announcements/*.vue",
  { eager: true },
);
const allAnnouncements: Announcement[] = Object.entries(_announcementsUnsorted)
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([path, mod]) => {
    const key = path.split("/").at(-1)!.replace(".vue", "");

    const dateParts = key.split("_", 1)[0]!.split("-").map(Number);
    const parsed = dateParts.length === 3
      ? new Date(dateParts[0]!, dateParts[1]! - 1, dateParts[2]!)
      : new Date(NaN);
    const date = isNaN(parsed.getTime()) ? undefined : parsed;

    return {
      key,
      component: mod.default,
      date,
      meta: mod.meta,
    };
  });

const newAnnouncements = shallowRef<Announcement[]>([]);

function isWelcomeAnnouncement(key: string) {
  return key === allAnnouncements.at(0)!.key;
}

export function useAnnouncements() {
  const auth = useMealieAuth();
  const api = useUserApi();
  const { household } = useHouseholdSelf();
  const { group } = useGroupSelf();

  const announcementsEnabled = computed(
    () =>
      !!(
        auth.user.value?.showAnnouncements
        && household.value?.preferences?.showAnnouncements
        && group.value?.preferences?.showAnnouncements
      ),
  );

  function updateUnreadAnnouncements(lastReadKey: string) {
    newAnnouncements.value = allAnnouncements.filter(a => a.key > lastReadKey);
  }

  async function setLastRead(key: string) {
    const user = auth.user.value!;

    if (!user.lastReadAnnouncement && isWelcomeAnnouncement(key)) {
      // The welcome announcement is a special case: it's shown to new users and
      // all other announcements are marked as read when they view it
      key = allAnnouncements.at(-1)!.key;
      updateUnreadAnnouncements(key);
    }
    else {
      // Only mark this specific announcement as read in the current session
      newAnnouncements.value = newAnnouncements.value.filter(a => a.key !== key);
    }

    if (user.lastReadAnnouncement && key <= user.lastReadAnnouncement) {
      // Don't update the last read announcement if it's older than the current one
      return;
    }

    user.lastReadAnnouncement = key; // update immediately so we don't have to wait for the db
    await api.users.updateOne(
      user.id,
      {
        ...user,
        lastReadAnnouncement: key,
      },
      { suppressAlert: true },
    );
  }

  async function markAllAsRead() {
    setLastRead(allAnnouncements.at(-1)!.key);
    newAnnouncements.value = [];
  }

  function initUnreadAnnouncements() {
    const user = auth.user.value;

    // Only logged-in users can see announcements
    if (!user || !allAnnouncements.length) {
      newAnnouncements.value = [];
      return;
    }

    // If a user has never seen an announcement, show them only the welcome announcement
    if (!user.lastReadAnnouncement) {
      newAnnouncements.value = [allAnnouncements.at(0)!];
      return;
    }

    // Return all announcements newer than the last read announcement
    updateUnreadAnnouncements(user.lastReadAnnouncement);
  }

  initUnreadAnnouncements();

  // If the user changes, re-init
  let lastUserId = auth.user.value?.id;
  watch(auth.user, () => {
    if (auth.user.value?.id === lastUserId) {
      return;
    }

    lastUserId = auth.user.value?.id;
    initUnreadAnnouncements();
  });

  return {
    announcementsEnabled,
    newAnnouncements,
    allAnnouncements,
    setLastRead,
    markAllAsRead,
  };
}
