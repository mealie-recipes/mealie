/**
 * Coordinates the app-wide search shortcut ("/" or ⌘K / Ctrl+K) and the search buttons in
 * the shell.
 *
 * A page with its own search field (the recipe library) registers it so the shortcut focuses
 * that field; everywhere else the shortcut opens the quick-search dialog owned by AppHeader.
 */
const dialogRequests = ref(0);
let pageSearch: (() => void) | null = null;

export function useGlobalSearch() {
  function open() {
    if (pageSearch) {
      pageSearch();
      return;
    }
    dialogRequests.value++;
  }

  function openDialog() {
    dialogRequests.value++;
  }

  /** Route the shortcut to a page's own search field while the calling component is mounted */
  function registerPageSearch(focus: () => void) {
    onMounted(() => {
      pageSearch = focus;
    });
    onBeforeUnmount(() => {
      if (pageSearch === focus) {
        pageSearch = null;
      }
    });
  }

  return {
    open,
    openDialog,
    registerPageSearch,
    dialogRequests: readonly(dialogRequests),
  };
}

/** The search shortcut as this platform writes it */
export function searchShortcutLabel(): string {
  const isApple = typeof navigator !== "undefined" && /Mac|iPhone|iPad/.test(navigator.userAgent);
  return isApple ? "⌘K" : "Ctrl K";
}

/** True for the keystrokes that should open search: "/" outside of a text field, or ⌘K / Ctrl+K anywhere */
export function isSearchShortcut(e: KeyboardEvent): boolean {
  if ((e.metaKey || e.ctrlKey) && !e.altKey && !e.shiftKey && e.key.toLowerCase() === "k") {
    return true;
  }

  const target = e.target as HTMLElement | null;
  const typing = !!target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable);
  return e.key === "/" && !typing && !e.metaKey && !e.ctrlKey && !e.altKey;
}
