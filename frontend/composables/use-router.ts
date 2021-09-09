import { useRoute, WritableComputedRef, computed } from "@nuxtjs/composition-api";

export function useRouterQuery(query: string) {
  const router = useRoute();
  // TODO FUTURE: Remove when migrating to Vue 3

  const param: WritableComputedRef<string> = computed({
    get(): string {
      // @ts-ignore
      return router.value?.query[query] || "";
    },
    set(v: string): void {
      router.value.query[query] = v;
    },
  });

  return param;
}
