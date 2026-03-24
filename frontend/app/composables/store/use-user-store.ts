import type { Composer } from "vue-i18n";
import { useReadOnlyStore } from "../partials/use-store-factory";
import { useRequests } from "../api/api-client";
import type { UserSummary } from "~/lib/api/types/user";
import { BaseCRUDAPIReadOnly } from "~/lib/api/base/base-clients";

const store: Ref<UserSummary[]> = ref([]);
const loading = ref(false);

export function resetUserStore() {
  store.value = [];
  loading.value = false;
}

class GroupUserAPIReadOnly extends BaseCRUDAPIReadOnly<UserSummary> {
  baseRoute = "/api/groups/members";
  itemRoute = (idOrUsername: string | number) => `/groups/members/${idOrUsername}`;
}

export const useUserStore = function (i18n?: Composer) {
  const requests = useRequests(i18n);
  const api = new GroupUserAPIReadOnly(requests);

  return useReadOnlyStore<UserSummary>("user", store, loading, api, { orderBy: "full_name" });
};
