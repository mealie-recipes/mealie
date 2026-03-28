import { useHouseholdSelf } from "~/composables/use-households";
import { useGroupSelf } from "~/composables/use-groups";

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

    const parsed = new Date(key.split("_", 1)[0]);
    const date = isNaN(parsed.getTime()) ? undefined : parsed;

    return {
      key,
      component: mod.default,
      date,
      meta: mod.meta,
    };
  });

const newAnnouncements = shallowRef<Announcement[]>([]);

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

    // Return all announcements newer than the last read announcement
    newAnnouncements.value = allAnnouncements.filter(a => a.key > user.lastReadAnnouncement!);
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
