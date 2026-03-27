import { useHouseholdSelf } from "~/composables/use-households";
import { useGroupSelf } from "~/composables/use-groups";

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

  const newAnnouncements = ref<string[] | undefined>();
  function refreshUnreadAnnouncements() {
    if (!auth.user.value) {
      newAnnouncements.value = undefined;
    }

    newAnnouncements.value = []; // TODO
  }

  refreshUnreadAnnouncements();
  watch(() => auth.user, () => {
    refreshUnreadAnnouncements();
  });

  return {
    announcementsEnabled,
    newAnnouncements,
  };
}
