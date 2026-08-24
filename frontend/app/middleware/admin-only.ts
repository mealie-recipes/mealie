export default defineNuxtRouteMiddleware(() => {
  const { user } = useMealieAuth();
  // If the user is not an admin redirect to the home page
  if (!user.value?.admin) {
    navigateTo("/");
  }
});
