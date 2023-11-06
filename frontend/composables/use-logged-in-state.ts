import { computed, useContext, useRoute } from "@nuxtjs/composition-api";

export const useLoggedInState = function () {
  const { $auth } = useContext();
  const route = useRoute();

  const loggedIn = computed(() => $auth.loggedIn);
  const isOwnGroup = computed(() => {
    if (!route.value.params.groupSlug) {
      return loggedIn.value;
    } else {
      return loggedIn.value && $auth.user?.groupSlug === route.value.params.groupSlug;
    }
  });

  return { loggedIn, isOwnGroup };
}
