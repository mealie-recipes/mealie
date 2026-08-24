export default defineNuxtRouteMiddleware(() => {
  const { user } = useMealieAuth();
  // If the user is not allowed to manage group settings redirect to the home page
  if (!user.value?.canManage) {
    console.warn("User is not allowed to manage group settings");
    navigateTo("/");
  }
});
