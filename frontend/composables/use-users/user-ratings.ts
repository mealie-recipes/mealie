import { ref, useContext } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { UserRatingSummary } from "~/lib/api/types/user";

const userRatings = ref<UserRatingSummary[]>([]);
const loading = ref(false);
const ready = ref(false);

export const useUserSelfRatings = function () {
  const { $auth } = useContext();
  const api = useUserApi();

  async function refreshUserRatings() {
    if (!$auth.user || loading.value) {
      return;
    }

    loading.value = true;
    const { data } = await api.users.getSelfRatings();
    userRatings.value = data?.ratings || [];
    loading.value = false;
    ready.value = true;
  }

  async function setRating(slug: string, rating: number | null, isFavorite: boolean | null) {
    loading.value = true;
    const userId = $auth.user?.id || "";
    await api.users.setRating(userId, slug, rating, isFavorite);
    loading.value = false;
    await refreshUserRatings();
  }

  if (!ready.value) {
    refreshUserRatings();
  }

  return {
    userRatings,
    refreshUserRatings,
    setRating,
    ready,
  }
}
