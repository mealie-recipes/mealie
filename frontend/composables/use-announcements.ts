import { useHouseholdSelf } from "~/composables/use-households";
import { useGroupSelf } from "~/composables/use-groups";

export type AnnouncementMeta = {
  title: string | undefined;
};

export type Announcement = {
  key: string;
  component: Component;
  meta: AnnouncementMeta | undefined;
};

const _announcementsUnsorted = import.meta.glob<{ default: Component; meta?: AnnouncementMeta }>(
  "~/components/Domain/Announcement/Announcements/*.vue",
  { eager: true },
);
const allAnnouncements: Announcement[] = Object.entries(_announcementsUnsorted)
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([path, mod]) => ({
    key: path.split("/").at(-1)!.replace(".vue", ""),
    component: mod.default,
    meta: mod.meta,
  }));

export function useAnnouncements() {
  const auth = useMealieAuth();
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

  function refreshUnreadAnnouncements() {
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

    newAnnouncements.value = []; // TODO
  }

  refreshUnreadAnnouncements();
  watch(auth.user, () => {
    refreshUnreadAnnouncements();
  });

  return {
    announcementsEnabled,
    newAnnouncements,
    allAnnouncements,
  };
}
