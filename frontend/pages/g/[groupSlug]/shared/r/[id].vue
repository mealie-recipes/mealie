<template>
  <div>
    <client-only>
      <RecipePage
        v-if="recipe"
        v-model="recipe"
      />
    </client-only>
  </div>
</template>

<script setup lang="ts">
import RecipePage from "~/components/Domain/Recipe/RecipePage/RecipePage.vue";
import { usePublicApi } from "~/composables/api/api-client";

definePageMeta({
  layout: "basic",
});

const $auth = useMealieAuth();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");

const router = useRouter();
const recipeId = route.params.id as string;
const api = usePublicApi();

const title = ref(route.meta?.title ?? "");
useSeoMeta({
  title,
});

const { data: recipe } = await useAsyncData("recipe", async () => {
  const { data, error } = await api.shared.getShared(recipeId);

  if (error) {
    console.error("error loading recipe -> ", error);
    router.push(`/g/${groupSlug.value}`);
  }

  if (data) {
    title.value = data?.name || "";
  }

  return data;
});
</script>
