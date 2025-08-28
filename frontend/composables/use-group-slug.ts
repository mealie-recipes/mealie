export const useGroupSlug = function () {
  const $auth = useMealieAuth();
  const route = useRoute();

  const groupSlug = computed<string | null>(() => {
    if (route.params.groupSlug) {
      return route.params.groupSlug as string;
    }
    else {
      return $auth.user.value?.groupSlug ?? null;
    }
  });

  return groupSlug;
};
