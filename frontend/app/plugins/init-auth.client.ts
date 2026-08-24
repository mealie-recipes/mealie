export default defineNuxtPlugin({
  async setup() {
    const auth = useAuthBackend();

    console.debug("Initializing auth plugin");
    await auth.getSession();
    console.debug("Auth plugin initialized");
  },
});
