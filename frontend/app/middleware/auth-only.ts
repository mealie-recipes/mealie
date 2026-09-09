import { isSafeRedirectTarget } from "~/lib/validators/redirect";

export default defineNuxtRouteMiddleware((to) => {
  const { loggedIn } = useMealieAuth();

  if (!loggedIn.value) {
    const redirect = isSafeRedirectTarget(to.fullPath) ? `?redirect=${encodeURIComponent(to.fullPath)}` : "";
    return navigateTo(`/login${redirect}`, { redirectCode: 302 });
  }
});
