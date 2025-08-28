import { usePublicExploreApi } from "~/composables/api";
import { useGroupSlug } from "~/composables/use-group-slug";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import type { ReadGroupPreferences } from "~/lib/api/types/user";

const preferencesRef = ref<ReadGroupPreferences | null>(null);
const preferencesGroupSlug = ref<string | null>(null);
const loading = ref(false);

export const useGroupPreferences = function () {
  const groupSlug = useGroupSlug();
  const { isOwnGroup } = useLoggedInState();
  const i18n = useI18n();

  const groupPreferences = computed(() => {
    if (!groupSlug.value) {
      return null;
    }
    if (preferencesRef.value && preferencesGroupSlug.value === groupSlug.value) {
      return preferencesRef.value;
    }
    if (loading.value) {
      return preferencesRef.value;
    }

    // fetch new group preferences
    if (isOwnGroup.value) {
      const { group } = useGroupSelf(i18n);
      preferencesRef.value = group.value?.preferences ?? null;
      console.log(preferencesRef.value);
    }
    else {
      loading.value = true;
      const api = usePublicExploreApi(groupSlug.value, i18n);
      api.explore.groups.getPreferences(groupSlug.value).then(
        ({ data }) => { preferencesRef.value = data; }
      ).finally(() => { loading.value = false; });
    }

    preferencesGroupSlug.value = groupSlug.value;
    return preferencesRef.value;
  });

  return {
    groupPreferences,
  };
}
