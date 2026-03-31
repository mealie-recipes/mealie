export function useScrollPosition() {
  const router = useRouter();
  const scrollPositions = new Map<string, number>();

  let observer: MutationObserver | null = null;
  let timeout: ReturnType<typeof setTimeout> | null = null;
  let fallback: ReturnType<typeof setTimeout> | null = null;

  const unregisterBefore = router.beforeEach((to, from) => {
    scrollPositions.set(from.path, document.documentElement.scrollTop);
  });

  const unregisterAfter = router.afterEach((to, from, failure) => {
    if (failure) return;

    if (window.history.state?.forward !== from.fullPath) return;

    const savedPosition = scrollPositions.get(to.path);
    if (!savedPosition) return;

    observer?.disconnect();
    if (timeout) clearTimeout(timeout);
    if (fallback) clearTimeout(fallback);

    observer = new MutationObserver(() => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        clearTimeout(fallback);
        observer.disconnect();
        document.documentElement.scrollTop = savedPosition;
      }, 100);
    });

    fallback = setTimeout(() => {
      clearTimeout(timeout);
      observer.disconnect();
      document.documentElement.scrollTop = savedPosition;
    }, 500);

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  });

  onUnmounted(() => {
    unregisterBefore();
    unregisterAfter();
    observer?.disconnect();
    if (timeout) clearTimeout(timeout);
    if (fallback) clearTimeout(fallback);
  });
}
