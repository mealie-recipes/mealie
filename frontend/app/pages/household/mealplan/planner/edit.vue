<template>
  <div>
    <GroupMealPlanEntryDialog
      v-model="dialog.open"
      :entry="dialog.entry"
      :date="dialog.date"
      @create="actions.createOne($event)"
      @update="actions.updateOne($event)"
    />
    <v-row>
      <v-col
        v-for="(plan, index) in mealplans"
        :key="index"
        cols="12"
        sm="12"
        md="6"
        lg="4"
        xl="3"
        xxl="2"
        class="col-borders my-1 d-flex flex-column"
      >
        <v-card class="mb-2 border-left-primary rounded-sm pa-2">
          <p class="pl-2 mb-1">
            {{ $d(plan.date, "short") }}
          </p>
        </v-card>
        <VueDraggable
          v-model="mealplansByDate[plan.date.toString()]"
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
          <v-card
            v-for="mealplan in mealplansByDate[plan.date.toString()]"
            :key="mealplan.id"
            class="my-1"
            :class="{ handle: $vuetify.display.smAndUp }"
          >
            <v-list-item lines="three" @click="editMeal(mealplan)">
              <template #prepend>
                <v-avatar>
                  <RecipeCardImage
                    v-if="mealplan.recipe"
                    :recipe-id="mealplan.recipe.id!"
                    tiny
                    icon-size="25"
                    :slug="mealplan.recipe ? mealplan.recipe.slug : ''"
                  />
                  <v-icon v-else>
                    {{ $globals.icons.primary }}
                  </v-icon>
                </v-avatar>
              </template>
              <v-list-item-title class="mb-1">
                {{ mealplan.recipe ? mealplan.recipe.name : mealplan.title }}
              </v-list-item-title>
              <v-list-item-subtitle style="min-height: 16px">
                {{ mealplan.recipe ? mealplan.recipe.description + " " : mealplan.text }}
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
        </VueDraggable>
        <!-- Day Column Actions -->
        <div class="d-flex justify-end mt-auto">
          <BaseButtonGroup
            :buttons="[
              {
                icon: $globals.icons.diceMultiple,
                text: $t('meal-plan.random-meal'),
                event: 'random',
                children: [
                  {
                    icon: $globals.icons.diceMultiple,
                    text: $t('meal-plan.breakfast'),
                    event: 'randomBreakfast',
                  },
                  {
                    icon: $globals.icons.diceMultiple,
                    text: $t('meal-plan.lunch'),
                    event: 'randomLunch',
                  },
                  {
                    icon: $globals.icons.diceMultiple,
                    text: $t('meal-plan.side'),
                    event: 'randomSide',
                  },
                  {
                    icon: $globals.icons.diceMultiple,
                    text: $t('meal-plan.snack'),
                    event: 'randomSnack',
                  },
                  {
                    icon: $globals.icons.diceMultiple,
                    text: $t('meal-plan.drink'),
                    event: 'randomDrink',
                  },
                  {
                    icon: $globals.icons.diceMultiple,
                    text: $t('meal-plan.dessert'),
                    event: 'randomDessert',
                  },
                ],
              },
              {
                icon: $globals.icons.potSteam,
                text: $t('meal-plan.random-dinner'),
                event: 'randomDinner',
              },
              {
                icon: $globals.icons.bowlMixOutline,
                text: $t('meal-plan.random-side'),
                event: 'randomSide',
              },
              {
                icon: $globals.icons.createAlt,
                text: $t('general.new'),
                event: 'create',
              },
            ]"
            @create="openDialog(plan.date)"
            @random-breakfast="randomMeal(plan.date, 'breakfast')"
            @random-lunch="randomMeal(plan.date, 'lunch')"
            @random-dinner="randomMeal(plan.date, 'dinner')"
            @random-side="randomMeal(plan.date, 'side')"
            @random-snack="randomMeal(plan.date, 'snack')"
            @random-drink="randomMeal(plan.date, 'drink')"
            @random-dessert="randomMeal(plan.date, 'dessert')"
          />
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { format } from "date-fns";
import type { SortableEvent } from "sortablejs";
import { VueDraggable } from "vue-draggable-plus";
import type { MealsByDate } from "./view.vue";
import type { useMealplans } from "~/composables/use-group-mealplan";
import { usePlanTypeOptions, getEntryTypeText } from "~/composables/use-group-mealplan";
import GroupMealPlanEntryDialog from "~/components/Domain/Household/GroupMealPlanEntryDialog.vue";
import RecipeCardImage from "~/components/Domain/Recipe/RecipeCardImage.vue";
import type { PlanEntryType, ReadPlanEntry } from "~/lib/api/types/meal-plan";
import { useUserApi } from "~/composables/api";

const props = defineProps<{
  mealplans: MealsByDate[];
  actions: ReturnType<typeof useMealplans>["actions"];
}>();

const api = useUserApi();

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
  const supportedEvents = ["drop", "touchend"];

  // Adapted From https://github.com/SortableJS/Vue.Draggable/issues/1029
  const ogEvent: DragEvent = (evt as any).originalEvent;

  if (ogEvent && ogEvent.type in supportedEvents) {
    // The drop was cancelled, unsure if anything needs to be done?
    console.log("Cancel Move Event");
  }
  else {
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
}

// =====================================================
// Meal Entry Dialog

const dialog = reactive({
  open: false,
  entry: null as ReadPlanEntry | null,
  date: null as Date | null,
});

function openDialog(date: Date) {
  dialog.entry = null;
  dialog.date = date;
  dialog.open = true;
}

function editMeal(mealplan: ReadPlanEntry) {
  if (!mealplan.entryType) return;

  dialog.entry = mealplan;
  dialog.date = null;
  dialog.open = true;
}

async function randomMeal(date: Date, type: PlanEntryType) {
  const { data } = await api.mealplans.setRandom({
    date: format(date, "yyyy-MM-dd"),
    entryType: type,
  });

  if (data) {
    props.actions.refreshAll();
  }
}

async function randomizeMeal(mealplan: ReadPlanEntry) {
  if (!mealplan.entryType) {
    return;
  }

  // Delete the current entry, then create a new random one with the same date and type
  const { data: deleted } = await api.mealplans.deleteOne(mealplan.id);
  if (deleted) {
    await api.mealplans.setRandom({
      date: mealplan.date,
      entryType: mealplan.entryType,
    });

    // Refresh either way: if setRandom failed we still need to reflect the deletion
    props.actions.refreshAll();
  }
}

const planTypeOptions = usePlanTypeOptions();
</script>
