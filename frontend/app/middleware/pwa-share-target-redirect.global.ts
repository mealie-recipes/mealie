export default defineNuxtRouteMiddleware((to) => {
  if (to.path === "/r/create/url") {
    const { user } = useMealieAuth();
    const groupSlug = user.value?.groupSlug;
    if (!groupSlug) {
      // Preserve the full path (including recipe_import_url query param) so the
      // login page can redirect back here after successful authentication.
      const redirect = encodeURIComponent(to.fullPath);
      return navigateTo(`/login?redirect=${redirect}`, { redirectCode: 302 });
    }
    return navigateTo(`/g/${groupSlug}${to.fullPath}`, { redirectCode: 302 });
  }
});
