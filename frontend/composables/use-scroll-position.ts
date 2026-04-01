const scrollPositions = new Map<string, number>();
const pagePositions = new Map<string, number>();

export function useScrollPosition() {
  const router = useRouter();

  let observer: MutationObserver | null = null;
  let timeout: ReturnType<typeof setTimeout> | null = null;
  let fallback: ReturnType<typeof setTimeout> | null = null;

  function savePosition(path: string, page: number) {
    scrollPositions.set(path, document.documentElement.scrollTop);
    pagePositions.set(path, page);
  }

  function getSavedPage(path: string): number | undefined {
    return pagePositions.get(path);
  }

  function restorePosition(path: string) {
    const savedPosition = scrollPositions.get(path);
    if (!savedPosition) return;

    observer?.disconnect();
    if (timeout) clearTimeout(timeout);
    if (fallback) clearTimeout(fallback);

    fallback = setTimeout(() => {
      if (timeout) clearTimeout(timeout);
      observer?.disconnect();
      document.documentElement.scrollTop = savedPosition;
    }, 500);

    observer = new MutationObserver(() => {
      if (timeout) clearTimeout(timeout);
      timeout = setTimeout(() => {
        if (fallback) clearTimeout(fallback);
        observer?.disconnect();
        document.documentElement.scrollTop = savedPosition;
      }, 100);
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  const unregisterBefore = router.beforeEach((to, from) => {
    scrollPositions.set(from.path, document.documentElement.scrollTop);
  });

  onUnmounted(() => {
    unregisterBefore();
    observer?.disconnect();
    if (timeout) clearTimeout(timeout);
    if (fallback) clearTimeout(fallback);
  });

  return {
    savePosition,
    getSavedPage,
    restorePosition,
  };
}
