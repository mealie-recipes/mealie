import { useUserApi } from "~/composables/api";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";

const allMealPlans = ref<ReadPlanEntry[]>([]);
const loading = ref(false);
const ready = ref(false);

export const useRecipeMealPlans = function () {
  const $auth = useMealieAuth();

  async function refreshMealPlans() {
    if (!$auth.user.value || loading.value) {
      return;
    }

    loading.value = true;
    const api = useUserApi();

    // Get today's date in YYYY-MM-DD format
    const today = new Date().toISOString().split("T")[0];

    // Fetch meal plans for today and future, plus unassigned meal plans
    const [scheduledResponse, unassignedResponse] = await Promise.all([
      api.mealplans.getAll(1, -1, { start_date: today }),
      api.mealplans.getUnassigned(),
    ]);

    const scheduledPlans = scheduledResponse.data?.items || [];
    const unassignedPlans = unassignedResponse.data || [];

    allMealPlans.value = [...scheduledPlans, ...unassignedPlans];

    loading.value = false;
    ready.value = true;
  }

  function getMealPlansForRecipe(recipeId: string): ReadPlanEntry[] {
    return allMealPlans.value.filter(plan => plan.recipeId === recipeId);
  }

  async function addToMealPlanWithoutDate(recipeId: string) {
    const api = useUserApi();
    const { response } = await api.mealplans.createOne({
      date: null,
      entryType: null,
      title: "",
      text: "",
      recipeId,
    });

    if (response?.status === 201) {
      await refreshMealPlans();
      return { success: true };
    }
    return { success: false };
  }

  async function removeMealPlanEntries(planIds: number[]) {
    const api = useUserApi();
    let allSuccess = true;

    for (const planId of planIds) {
      const { response } = await api.mealplans.deleteOne(planId);
      if (response?.status !== 200) {
        allSuccess = false;
      }
    }

    await refreshMealPlans();
    return { success: allSuccess };
  }

  if (!ready.value) {
    refreshMealPlans();
  }

  return {
    allMealPlans,
    getMealPlansForRecipe,
    addToMealPlanWithoutDate,
    removeMealPlanEntries,
    refreshMealPlans,
    ready,
  };
};
