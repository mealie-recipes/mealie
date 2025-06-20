export const useLoggedInState = function () {
  const $auth = useMealieAuth();
  const route = useRoute();

  const loggedIn = computed(() => $auth.loggedIn.value);
  const isOwnGroup = computed(() => {
    if (!route.params.groupSlug) {
      return loggedIn.value;
    }
    else {
      return loggedIn.value && $auth.user.value?.groupSlug === route.params.groupSlug;
    }
  });

  return { loggedIn, isOwnGroup };
};
