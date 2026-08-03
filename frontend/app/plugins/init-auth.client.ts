export default defineNuxtPlugin({
  async setup() {
    const auth = useAuthBackend();
    const { $appInfo } = useNuxtApp();

    console.debug("Initializing auth plugin");
    await auth.getSession({ allowProxyAuthProbe: Boolean($appInfo.enableProxyAuth) });
    console.debug("Auth plugin initialized");
  },
});
