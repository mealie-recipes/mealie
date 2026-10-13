<template>
  <div>
    <GroupMealPlanEntryDialog
      v-model="dialog.open"
      :entry="dialog.entry"
      :date="dialog.date"
      @create="actions.createOne($event)"
      @update="actions.updateOne($event)"
    />
    <MealPlanLayout :mealplans="mealplans">
      <template #default="{ day }">
        <MealPlanDay :day="day.date" :actions="actions" :recipes="day.recipes">
          <SpinTransition>
            <div v-if="day.sections.length" class="plan-day-meals">
              <SpinTransition>
                <div v-for="section in day.sections" :key="section.title">
                  <div class="plan-section">
                    {{ section.title }}
                  </div>
                  <SpinTransition>
                    <RecipeCardMobile
                      v-for="mealplan in section.meals"
                      :key="mealplan.id"
                      :recipe-id="mealplan.recipe ? mealplan.recipe.id! : ''"
                      class="mb-2"
                      :rating="mealplan.recipe ? mealplan.recipe.rating! : 0"
                      :slug="mealplan.recipe ? mealplan.recipe.slug! : mealplan.title!"
                      :description="mealplan.recipe ? mealplan.recipe.description! : mealplan.text!"
                      :name="mealplan.recipe ? mealplan.recipe.name! : mealplan.title!"
                      :image="mealplan.recipe ? mealplan.recipe.image! : undefined"
                      :tags="mealplan.recipe ? mealplan.recipe.tags! : []"
                      :context-menu-leading-items="[
                        {
                          title: $t('meal-plan.remove-from-plan'),
                          icon: $globals.icons.calendarRemove,
                          color: undefined,
                          event: 'mealplanRemove',
                          isPublic: false,
                        },
                        {
                          title: $t('meal-plan.edit-meal-plan'),
                          icon: $globals.icons.calendarEdit,
                          color: undefined,
                          event: 'mealplanEdit',
                          isPublic: false,
                        },
                      ]"
                      @mealplan-remove="actions.deleteOne(mealplan.id)"
                      @mealplan-edit="editMeal(mealplan)"
                    >
                      <template v-if="!mealplan.recipe" #context-menu>
                        <MealPlanNoteMenu
                          @mealplan-remove="actions.deleteOne(mealplan.id)"
                          @mealplan-edit="editMeal(mealplan)"
                        />
                      </template>
                    </RecipeCardMobile>
                  </SpinTransition>
                </div>
              </SpinTransition>
            </div>
            <div v-else class="plan-day-empty">
              {{ $t("recipe-library.nothing-planned") }}
            </div>
          </SpinTransition>
        </MealPlanDay>
      </template>
    </MealPlanLayout>
  </div>
</template>

<script setup lang="ts">
import MealPlanNoteMenu from "~/components/Domain/Mealplan/MealPlanNoteMenu.vue";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";
import type { MealsByDate } from "~/composables/use-group-mealplan";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";

defineProps<{
  mealplans: MealsByDate[];
  actions: ReturnType<typeof useMealplans>["actions"];
}>();

const dialog = reactive({
  open: false,
  entry: null as ReadPlanEntry | null,
  date: null as Date | null,
});

function editMeal(mealplan: ReadPlanEntry) {
  if (!mealplan.entryType) return;

  dialog.entry = mealplan;
  dialog.date = null;
  dialog.open = true;
}
</script>

<style scoped>
.plan-day-meals {
  margin-top: 4px;
}

.plan-section {
  padding: 12px 2px 8px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--mealie-text-tertiary);
}

.plan-day-empty {
  padding: 18px 2px 8px;
  font-size: 14px;
  color: var(--mealie-text-quaternary);
}
</style>
