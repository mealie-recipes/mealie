import { useLocalStorage } from "@vueuse/core";

/**
 * Whether the sidebar is open, or null to use the screen-size default.
 * The preference is shared between the household and admin layouts in this browser.
 */
export function useSidebarState() {
  const display = useDisplay();
  const preference = useLocalStorage<boolean | null>("sidebar-open", null);
  const sidebarQuery = useRouteQuery<string>("sidebar", "");

  return computed<boolean>({
    get: () => {
      if (sidebarQuery.value === "true") {
        return true;
      }
      if (sidebarQuery.value === "false") {
        return false;
      }
      return preference.value ?? display.lgAndUp.value;
    },
    set: (value: boolean) => {
      preference.value = value;
      if (sidebarQuery.value === "true" || sidebarQuery.value === "false") {
        sidebarQuery.value = String(value);
      }
    },
  });
}
