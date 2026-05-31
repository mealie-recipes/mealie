export default defineNuxtRouteMiddleware((to) => {
  const { user } = useMealieAuth();
  // this can only be used for routes that have a groupSlug parameter (e.g. /g/:groupSlug/...)
  if (to.params.groupSlug !== user.value?.groupSlug) {
    if (!user.value) {
      // Not authenticated - redirect to login preserving the intended URL so the user is returned here after login
      const redirect = encodeURIComponent(to.fullPath);
      return navigateTo(`/login?redirect=${redirect}`, { redirectCode: 302 });
    }
    // Authenticated but accessing a different group - redirect to their own group home
    return navigateTo(`/g/${user.value.groupSlug}`);
  }
});
