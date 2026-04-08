export function useRouterQuery(query: string) {
  const router = useRoute();
  // TODO FUTURE: Remove when migrating to Vue 3

  const param: WritableComputedRef<string> = computed({
    get(): string {
      console.log("Get Query Change");
      return router?.query[query] as string || "";
    },
    set(v: string): void {
      router.query[query] = v;
    },
  });

  return param;
}

export function useRouteQuery<T extends string | string[]>(name: string, defaultValue?: T) {
  const route = useRoute();
  const router = useRouter();

  return computed<any>({
    get() {
      const data = route.query[name];
      if (data == null) return defaultValue ?? null;
      return data;
    },
    set(v) {
      nextTick(() => {
        router.replace({ query: { ...route.query, [name]: v } });
      });
    },
  });
}
