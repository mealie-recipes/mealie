export const useCanOrganize = function () {
  const auth = useMealieAuth();

  return computed(() => !!auth.user.value?.canOrganize);
};
