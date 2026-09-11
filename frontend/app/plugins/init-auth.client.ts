export default defineNuxtPlugin({
  async setup() {
    const auth = useAuthBackend();

    console.debug("Initializing auth plugin");
    // Must come first: it hydrates the token from the cookie, which getSession checks before it
    // will bother asking the server who we are.
    auth.initTokenRefresh();
    await auth.getSession();
    console.debug("Auth plugin initialized");
  },
});
