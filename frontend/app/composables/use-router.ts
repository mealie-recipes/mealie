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
