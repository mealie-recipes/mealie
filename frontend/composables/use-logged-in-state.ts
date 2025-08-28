import { useGroupSlug } from "~/composables/use-group-slug";

export const useLoggedInState = function () {
  const $auth = useMealieAuth();
  const groupSlug = useGroupSlug();

  const loggedIn = computed(() => $auth.loggedIn.value);
  const isOwnGroup = computed(() => {
    if (!groupSlug.value) {
      return loggedIn.value;
    }
    else {
      return loggedIn.value && $auth.user.value?.groupSlug === groupSlug.value;
    }
  });

  return { loggedIn, isOwnGroup };
};
