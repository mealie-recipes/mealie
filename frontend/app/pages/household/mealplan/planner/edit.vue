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
      <template #default="{ plan, index, day }">
        <MealPlanDay :day="day.date" :recipes="day.recipes" :actions="actions" inline-actions>
          <VueDraggable
            v-model="mealplansByDate[plan.date.toString()]!"
            tag="div"
            handle=".handle"
            :delay="250"
            :delay-on-touch-only="true"
            group="meals"
            :data-index="index"
            :data-box="plan.date"
            style="min-height: 150px"
            @end="onMoveCallback"
          >
            <SpinTransition>
              <v-card
                v-for="mealplan in mealplansByDate[plan.date.toString()]"
                :key="mealplan.id"
                class="my-2 ml-4 mr-1"
                :class="{ handle: $vuetify.display.smAndUp }"
              >
                <RecipeCardLineItem
                  v-if="mealplan.recipe"
                  class="py-2"
                  :recipe="mealplan.recipe"
                  disable-link
                  @click="editMeal(mealplan)"
                />
                <v-list-item
                  v-else
                  class="py-2"
                  @click="editMeal(mealplan)"
                >
                  <template #prepend>
                    <v-avatar>
                      <v-icon>
                        {{ $globals.icons.primary }}
                      </v-icon>
                    </v-avatar>
                  </template>
                  <v-list-item-title>
                    {{ mealplan.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle v-if="mealplan.text">
                    {{ mealplan.text }}
                  </v-list-item-subtitle>
                </v-list-item>
                <v-divider class="mx-2" />
                <div class="py-2 px-2 d-flex" style="align-items: center">
                  <v-btn size="small" icon variant="text" :class="{ handle: !$vuetify.display.smAndUp }">
                    <v-icon>
                      {{ $globals.icons.arrowUpDown }}
                    </v-icon>
                  </v-btn>
                  <v-menu offset-y>
                    <template #activator="{ props: menuProps }">
                      <v-chip
                        v-bind="menuProps"
                        label
                        variant="elevated"
                        size="small"
                        color="accent"
                        @click.prevent
                      >
                        <v-icon start>
                          {{ $globals.icons.tags }}
                        </v-icon>
                        {{ getEntryTypeText(mealplan.entryType!) }}
                      </v-chip>
                    </template>
                    <v-list>
                      <v-list-item
                        v-for="mealType in planTypeOptions"
                        :key="mealType.value"
                        @click="actions.setType(mealplan, mealType.value)"
                      >
                        <v-list-item-title> {{ mealType.text }} </v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                  <v-btn
                    v-if="mealplan.recipe && mealplan.entryType"
                    class="ml-auto"
                    size="small"
                    variant="text"
                    icon
                    :title="$t('meal-plan.randomize-recipe')"
                    @click="randomizeMeal(mealplan)"
                  >
                    <v-icon>{{ $globals.icons.diceMultiple }}</v-icon>
                  </v-btn>
                  <v-btn :class="{ 'ml-auto': !mealplan.recipe || !mealplan.entryType }" size="small" variant="text" icon @click="actions.deleteOne(mealplan.id)">
                    <v-icon>{{ $globals.icons.delete }}</v-icon>
                  </v-btn>
                </div>
              </v-card>
            </SpinTransition>
          </VueDraggable>
        </MealPlanDay>
      </template>
    </MealPlanLayout>
  </div>
</template>

<script setup lang="ts">
import { format } from "date-fns";
import type { SortableEvent } from "sortablejs";
import { VueDraggable } from "vue-draggable-plus";
import GroupMealPlanEntryDialog from "~/components/Domain/Household/GroupMealPlanEntryDialog.vue";
import RecipeCardLineItem from "~/components/Domain/Recipe/RecipeCardLineItem.vue";
import { useUserApi } from "~/composables/api";
import type { MealsByDate, useMealplans } from "~/composables/use-group-mealplan";
import { getEntryTypeText, usePlanTypeOptions } from "~/composables/use-group-mealplan";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";

const props = defineProps<{
  mealplans: MealsByDate[];
  actions: ReturnType<typeof useMealplans>["actions"];
}>();

const api = useUserApi();
const planTypeOptions = usePlanTypeOptions();

// Local mutable meals object
const mealplansByDate = reactive<{ [date: string]: ReadPlanEntry[] }>({});
watch(
  () => props.mealplans,
  (plans) => {
    for (const plan of plans) {
      mealplansByDate[plan.date.toString()] = plan.meals ? [...plan.meals] : [];
    }
    // Remove any dates that no longer exist
    Object.keys(mealplansByDate).forEach((date) => {
      if (!plans.find(p => p.date.toString() === date)) {
        mealplansByDate[date] = [];
      }
    });
  },
  { immediate: true, deep: true },
);

function onMoveCallback(evt: SortableEvent) {
  // A Meal was moved, set the new date value and make an update request and refresh the meals
  const fromMealsByIndex = parseInt(evt.from.getAttribute("data-index") ?? "");
  const toMealsByIndex = parseInt(evt.to.getAttribute("data-index") ?? "");

  if (!isNaN(fromMealsByIndex) && !isNaN(toMealsByIndex)) {
    const destDate = props.mealplans[toMealsByIndex].date;
    const mealData = mealplansByDate[destDate.toString()][evt.newIndex as number];

    mealData.date = format(destDate, "yyyy-MM-dd");

    props.actions.updateOne(mealData);
  }
}

// =====================================================
// Meal Entry Dialog

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

async function randomizeMeal(mealplan: ReadPlanEntry) {
  if (!mealplan.entryType) {
    return;
  }

  // Create the new random entry first, so a failure here doesn't lose the current entry
  const { data: created } = await api.mealplans.setRandom({
    date: mealplan.date,
    entryType: mealplan.entryType,
  });

  if (created) {
    await api.mealplans.deleteOne(mealplan.id);
    props.actions.refreshAll();
  }
}
</script>
