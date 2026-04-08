export default defineNuxtRouteMiddleware((to) => {
  if (to.path === "/r/create/url") {
    const { user } = useMealieAuth();
    const groupSlug = user.value?.groupSlug;
    if (!groupSlug) {
      return navigateTo("/login", { redirectCode: 301 });
    }
    return navigateTo(`/g/${groupSlug}${to.fullPath}`, { redirectCode: 301 });
  }
});
