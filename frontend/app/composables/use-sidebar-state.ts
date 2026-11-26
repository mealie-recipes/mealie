import { StorageSerializers, useLocalStorage } from "@vueuse/core";
import { ref } from "vue";
import { useRouteQuery } from "~/composables/use-router";

/**
 * Whether the sidebar is open, or null to use the screen-size default.
 * The preference is shared between the household and admin layouts in this browser.
 */
export function useSidebarState() {
  const display = useDisplay();
  const drawerState = ref(false);
  const preference = useLocalStorage<boolean | null>("sidebar-open", null, {
    serializer: StorageSerializers.boolean,
  });
  const sidebarQuery = useRouteQuery<string>("sidebar", "");

  const sidebar = computed<boolean>({
    get: () => {
      if (sidebarQuery.value === "true") {
        return true;
      }
      if (sidebarQuery.value === "false") {
        return false;
      }
      if (!display.lgAndUp.value) {
        return drawerState.value;
      }
      return preference.value ?? true;
    },
    set: (value: boolean) => {
      if (display.lgAndUp.value) {
        preference.value = value;
      } else {
        // Vuetify updates the temporary drawer during route and breakpoint changes.
        drawerState.value = value;
      }
      if (sidebarQuery.value === "true" || sidebarQuery.value === "false") {
        sidebarQuery.value = String(value);
      }
    },
  });

  return sidebar;
}
