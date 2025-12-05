<template>
  <div>
    <!-- Create Meal Dialog -->
    <BaseDialog
      v-model="state.dialog"
      :title="newMeal.existing ? $t('meal-plan.update-this-meal-plan') : $t('meal-plan.create-a-new-meal-plan')"
      :submit-text="newMeal.existing ? $t('general.update') : $t('general.create')"
      color="primary"
      :icon="$globals.icons.foods"
      :submit-disabled="isCreateDisabled"
      can-submit
      @submit="
        () => {
          if (newMeal.existing) {
            actions.updateOne({ ...newMeal, date: newMealDateString });
          }
          else {
            actions.createOne({ ...newMeal, date: newMealDateString });
          }
          resetDialog();
        }
      "
      @close="resetDialog()"
    >
      <v-card-text class="pb-2">
        <v-date-picker
          v-model="newMeal.date"
          class="mx-auto"
          hide-header
          show-adjacent-months
          color="primary"
          :first-day-of-week="firstDayOfWeek"
          :local="$i18n.locale"
        />
        <v-card-text class="pb-0">
          <v-select
            v-model="newMeal.entryType"
            :return-object="false"
            :items="planTypeOptions"
            :label="$t('recipe.entry-type')"
            item-title="text"
            item-value="value"
          />
          <v-autocomplete
            v-if="!dialog.note"
            v-model="newMeal.recipeId"
            v-model:search="search.query.value"
            :label="$t('meal-plan.meal-recipe')"
            :items="search.data.value"
            :custom-filter="normalizeFilter"
            :loading="search.loading.value"
            cache-items
            item-title="name"
            item-value="id"
            :return-object="false"
            :rules="[requiredRule]"
          />
          <template v-else>
            <v-text-field v-model="newMeal.title" :rules="[requiredRule]" :label="$t('meal-plan.meal-title')" />
            <v-textarea v-model="newMeal.text" rows="2" :label="$t('meal-plan.meal-note')" />
          </template>
        </v-card-text>
        <v-card-actions class="py-0 px-4">
          <v-switch v-model="dialog.note" class="mt-n3 mb-n4" :label="$t('meal-plan.note-only')" />
        </v-card-actions>
      </v-card-text>
    </BaseDialog>
    <v-row>
      <v-col
        v-for="(plan, index) in mealplans"
        :key="index"
        cols="12"
        sm="12"
        md="3"
        lg="3"
        xl="2"
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
                <template #activator="{ props }">
                  <v-chip
                    v-bind="props"
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
              <v-btn class="ml-auto" size="small" variant="text" icon @click="actions.deleteOne(mealplan.id)">
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

<script lang="ts">
import { format } from "date-fns";
import type { SortableEvent } from "sortablejs";
import { VueDraggable } from "vue-draggable-plus";
import type { MealsByDate } from "./types";
import type { useMealplans } from "~/composables/use-group-mealplan";
import { usePlanTypeOptions, getEntryTypeText } from "~/composables/use-group-mealplan";
import RecipeCardImage from "~/components/Domain/Recipe/RecipeCardImage.vue";
import type { PlanEntryType, UpdatePlanEntry } from "~/lib/api/types/meal-plan";
import { useUserApi } from "~/composables/api";
import { useHouseholdSelf } from "~/composables/use-households";
import { normalizeFilter } from "~/composables/use-utils";
import { useRecipeSearch } from "~/composables/recipes/use-recipe-search";

export default defineNuxtComponent({
  components: {
    VueDraggable,
    RecipeCardImage,
  },
  props: {
    mealplans: {
      type: Array as () => MealsByDate[],
      required: true,
    },
    actions: {
      type: Object as () => ReturnType<typeof useMealplans>["actions"],
      required: true,
    },
  },
  setup(props) {
    const api = useUserApi();
    const $auth = useMealieAuth();
    const { household } = useHouseholdSelf();
    const requiredRule = (value: any) => !!value || "Required.";

    const state = ref({
      dialog: false,
    });

    const firstDayOfWeek = computed(() => {
      return household.value?.preferences?.firstDayOfWeek || 0;
    });

    // Local mutable meals object
    const mealplansByDate = reactive<{ [date: string]: UpdatePlanEntry[] }>({});
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
    // New Meal Dialog

    const dialog = reactive({
      loading: false,
      error: false,
      note: false,
    });

    watch(dialog, () => {
      if (dialog.note) {
        newMeal.recipeId = undefined;
      }
    });

    const newMeal = reactive({
      date: new Date(Date.now() - new Date().getTimezoneOffset() * 60000),
      title: "",
      text: "",
      recipeId: undefined as string | undefined,
      entryType: "dinner" as PlanEntryType,
      existing: false,
      id: 0,
      groupId: "",
      userId: $auth.user.value?.id || "",
    });

    const newMealDateString = computed(() => {
      return format(newMeal.date, "yyyy-MM-dd");
    });

    const isCreateDisabled = computed(() => {
      if (dialog.note) {
        return !newMeal.title.trim();
      }
      return !newMeal.recipeId;
    });

    function openDialog(date: Date) {
      newMeal.date = date;
      state.value.dialog = true;
    }

    function editMeal(mealplan: UpdatePlanEntry) {
      const { date, title, text, entryType, recipeId, id, groupId, userId } = mealplan;
      if (!entryType) return;

      const [year, month, day] = date.split("-").map(Number);
      newMeal.date = new Date(year, month - 1, day);
      newMeal.title = title || "";
      newMeal.text = text || "";
      newMeal.recipeId = recipeId || undefined;
      newMeal.entryType = entryType;
      newMeal.existing = true;
      newMeal.id = id;
      newMeal.groupId = groupId;
      newMeal.userId = userId || $auth.user.value?.id || "";

      state.value.dialog = true;
      dialog.note = !recipeId;
    }

    function resetDialog() {
      newMeal.date = new Date(Date.now() - new Date().getTimezoneOffset() * 60000);
      newMeal.title = "";
      newMeal.text = "";
      newMeal.entryType = "dinner";
      newMeal.recipeId = undefined;
      newMeal.existing = false;
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

    // =====================================================
    // Search

    const search = useRecipeSearch(api);
    const planTypeOptions = usePlanTypeOptions();

    onMounted(async () => {
      await search.trigger();
    });

    return {
      state,
      onMoveCallback,
      planTypeOptions,
      getEntryTypeText,
      requiredRule,
      isCreateDisabled,
      normalizeFilter,

      // Dialog
      dialog,
      newMeal,
      newMealDateString,
      openDialog,
      editMeal,
      resetDialog,
      randomMeal,

      // Search
      search,
      firstDayOfWeek,
      mealplansByDate,
    };
  },
});
</script>
