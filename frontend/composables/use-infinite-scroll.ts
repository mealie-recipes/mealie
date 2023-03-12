import {  ref, Ref } from "@nuxtjs/composition-api"
import { useDebounceFn } from "@vueuse/core"


type InfiniteScrollOptions ={
  page: Ref<number>
  perPage: Ref<number>
  total: Ref<number>
  locked?: Ref<boolean>
  data: Ref<any[]>
  callback: () => Promise<void>
}




export function useInfiniteScroll(opts: InfiniteScrollOptions) {
  const loading = ref(false)

  const { data, callback, locked, page, total} = opts

  const onScrollRaw = () => {
    console.log("onScroll")
    const { length } = data.value


    // don't run if:
    // - already loading
    // - there's nothing more to load
    if (loading.value || locked?.value || total.value !== -1 && length >= total.value) {
      return
    }

    // load more items
    loading.value = true
    page.value = page.value + 1
    callback().then(() => {
      loading.value = false
    })
  }

  const onScroll = useDebounceFn(onScrollRaw, 100)

  return {
    onScroll,
    loading,
  }
}
