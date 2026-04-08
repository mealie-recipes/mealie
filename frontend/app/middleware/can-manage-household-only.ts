const { user } = useMealieAuth();
export default defineNuxtRouteMiddleware(() => {
  // If the user is not allowed to manage group settings redirect to the home page
  if (!user.value?.canManageHousehold) {
    navigateTo("/");
  }
});
