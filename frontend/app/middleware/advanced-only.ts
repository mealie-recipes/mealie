export default defineNuxtRouteMiddleware(() => {
  const { user } = useMealieAuth();
  // If the user is not allowed to access advanced features redirect to the home page
  if (!user.value?.advanced) {
    console.warn("User is not allowed to access advanced features");
    navigateTo("/");
  }
});
