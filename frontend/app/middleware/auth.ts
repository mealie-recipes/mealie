export default defineNuxtRouteMiddleware((to) => {
  const { loggedIn } = useMealieAuth();
  // If the user is not logged in redirect to the login page, then back here once they are
  if (!loggedIn.value) {
    return navigateTo({ path: "/login", query: { redirect: to.fullPath } });
  }
});
