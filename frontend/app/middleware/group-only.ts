export default defineNuxtRouteMiddleware((to) => {
  const { user } = useMealieAuth();
  // this can only be used for routes that have a groupSlug parameter (e.g. /g/:groupSlug/...)
  if (to.params.groupSlug !== user.value?.groupSlug) {
    navigateTo("/");
  }
});
