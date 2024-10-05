import { ref, Ref } from "@nuxtjs/composition-api";
import { useReadOnlyStore } from "../partials/use-store-factory";
import { UserSummary } from "~/lib/api/types/user";
import { useRequests } from "../api/api-client";
import { BaseCRUDAPIReadOnly } from "~/lib/api/base/base-clients";

const store: Ref<UserSummary[]> = ref([]);
const loading = ref(false);

class GroupUserAPIReadOnly extends BaseCRUDAPIReadOnly<UserSummary> {
  baseRoute = "/groups/members";
  itemRoute = (idOrUsername: string | number) => `/groups/members/${idOrUsername}`;
}

export const useUserStore = function () {
  const requests = useRequests();
  const api = new GroupUserAPIReadOnly(requests);

  return useReadOnlyStore<UserSummary>(store, loading, api);
}
