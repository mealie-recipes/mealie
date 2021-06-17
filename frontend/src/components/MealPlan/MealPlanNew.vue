<template>
  <v-card>
    <v-card-title class=" headline">
      {{ $t("meal-plan.create-a-new-meal-plan") }}
      <v-btn color="info" class="ml-auto" @click="setQuickWeek()">
        <v-icon left> {{ $globals.icons.calendarMinus }} </v-icon>
        {{ $t("meal-plan.quick-week") }}
      </v-btn>
    </v-card-title>

    <v-divider></v-divider>
    <v-card-text>
      <v-row dense>
        <v-col cols="12" lg="6" md="6" sm="12">
          <v-menu
            ref="menu1"
            v-model="menu1"
            :close-on-content-click="true"
            transition="scale-transition"
            offset-y
            max-width="290px"
            min-width="290px"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="startComputedDateFormatted"
                :label="$t('meal-plan.start-date')"
                persistent-hint
                :prepend-icon="$globals.icons.calendarMinus"
                readonly
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <DatePicker v-model="startDate" no-title @input="menu2 = false" />
          </v-menu>
        </v-col>
        <v-col cols="12" lg="6" md="6" sm="12">
          <v-menu
            ref="menu2"
            v-model="menu2"
            :close-on-content-click="true"
            transition="scale-transition"
            offset-y
            max-width="290px"
            min-width="290px"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="endComputedDateFormatted"
                :label="$t('meal-plan.end-date')"
                persistent-hint
                :prepend-icon="$globals.icons.calendarMinus"
                readonly
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <DatePicker v-model="endDate" no-title @input="menu2 = false" />
          </v-menu>
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-text v-if="startDate">
      <MealPlanCard v-model="planDays" />
    </v-card-text>
    <v-row align="center" justify="end">
      <v-card-actions class="mr-5">
        <TheButton edit @click="random" v-if="planDays.length > 0" text>
          <template v-slot:icon>
            {{ $globals.icons.diceMultiple }}
          </template>
          {{ $t("general.random") }}
        </TheButton>
        <TheButton create @click="save" :disabled="planDays.length == 0" />
      </v-card-actions>
    </v-row>
  </v-card>
</template>

<script>
const CREATE_EVENT = "created";
import DatePicker from "@/components/FormHelpers/DatePicker";
import { api } from "@/api";
import { utils } from "@/utils";
import MealPlanCard from "./MealPlanCard";
export default {
  components: {
    MealPlanCard,
    DatePicker,
  },
  data() {
    return {
      isLoading: false,
      planDays: [],
      items: [],

      // Dates
      startDate: null,
      endDate: null,
      menu1: false,
      menu2: false,
      usedRecipes: [1],
    };
  },

  watch: {
    dateDif() {
      this.planDays = [];
      for (let i = 0; i < this.dateDif; i++) {
        this.planDays.push({
          date: this.getDate(i),
          meals: [
            {
              name: "",
              slug: "empty",
              description: "empty",
            },
          ],
        });
      }
    },
  },
  async mounted() {
    await this.$store.dispatch("requestCurrentGroup");
    await this.$store.dispatch("requestAllRecipes");
    await this.buildMealStore();
  },

  computed: {
    groupSettings() {
      return this.$store.getters.getCurrentGroup;
    },
    actualStartDate() {
      if (!this.startDate) return null;
      return Date.parse(this.startDate.replaceAll("-", "/"));
    },
    actualEndDate() {
      if (!this.endDate) return null;
      return Date.parse(this.endDate.replaceAll("-", "/"));
    },
    dateDif() {
      if (!this.actualEndDate || !this.actualStartDate) return null;
      let dateDif = (this.actualEndDate - this.actualStartDate) / (1000 * 3600 * 24) + 1;
      if (dateDif < 1) {
        return null;
      }
      return dateDif;
    },
    startComputedDateFormatted() {
      return this.formatDate(this.actualStartDate);
    },
    endComputedDateFormatted() {
      return this.formatDate(this.actualEndDate);
    },
    filteredRecipes() {
      const recipes = this.items.filter(x => !this.usedRecipes.includes(x));
      return recipes.length > 0 ? recipes : this.items;
    },
    allRecipes() {
      return this.$store.getters.getAllRecipes;
    },
  },

  methods: {
    async buildMealStore() {
      const categories = Array.from(this.groupSettings.categories, x => x.name);
      this.items = await api.recipes.getAllByCategory(categories);

      if (this.items.length === 0) {
        this.items = this.allRecipes;
      }
    },
    getRandom(list) {
      return list[Math.floor(Math.random() * list.length)];
    },
    random() {
      this.usedRecipes = [1];
      this.planDays.forEach((_, index) => {
        let recipe = this.getRandom(this.filteredRecipes);
        this.planDays[index]["meals"][0]["slug"] = recipe.slug;
        this.planDays[index]["meals"][0]["name"] = recipe.name;
        this.usedRecipes.push(recipe);
      });
    },
    getDate(index) {
      const dateObj = new Date(this.actualStartDate.valueOf() + 1000 * 3600 * 24 * index);
      return utils.getDateAsPythonDate(dateObj);
    },
    async save() {
      const mealBody = {
        group: this.groupSettings.name,
        startDate: this.startDate,
        endDate: this.endDate,
        planDays: this.planDays,
      };
      if (await api.mealPlans.create(mealBody)) {
        this.$emit(CREATE_EVENT);
        this.planDays = [];
        this.startDate = null;
        this.endDate = null;
      }
    },
    formatDate(date) {
      if (!date) return null;

      return this.$d(date);
    },
    getNextDayOfTheWeek(dayName, excludeToday = true, refDate = new Date()) {
      const dayOfWeek = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"].indexOf(dayName.slice(0, 3).toLowerCase());
      if (dayOfWeek < 0) return;
      refDate.setUTCHours(0, 0, 0, 0);
      refDate.setDate(refDate.getDate() + +!!excludeToday + ((dayOfWeek + 7 - refDate.getDay() - +!!excludeToday) % 7));
      return refDate;
    },
    setQuickWeek() {
      const nextMonday = this.getNextDayOfTheWeek("Monday", false);
      const nextEndDate = new Date(nextMonday);
      nextEndDate.setDate(nextEndDate.getDate() + 4);

      this.startDate = utils.getDateAsPythonDate(nextMonday);
      this.endDate = utils.getDateAsPythonDate(nextEndDate);
    },
  },
};
</script>
