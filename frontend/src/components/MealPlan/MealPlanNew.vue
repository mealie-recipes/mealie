<template>
  <v-card>
    <v-card-title class=" headline">
      {{ $t("meal-plan.create-a-new-meal-plan") }}
      <v-btn color="info" class="ml-auto" @click="setQuickWeek()">
        <v-icon left>mdi-calendar-minus</v-icon> {{$t('meal-plan.quick-week')}}
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
                prepend-icon="mdi-calendar"
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
                prepend-icon="mdi-calendar"
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
      <MealPlanCard v-model="meals" />
    </v-card-text>
    <v-row align="center" justify="end">
      <v-card-actions class="mr-5">
        <v-btn color="success" @click="random" v-if="meals.length > 0" text>
          {{ $t("general.random") }}
        </v-btn>
        <v-btn color="success" @click="save" text :disabled="meals.length == 0">
          {{ $t("general.save") }}
        </v-btn>
      </v-card-actions>
    </v-row>
  </v-card>
</template>

<script>
const CREATE_EVENT = "created";
import DatePicker from "@/components/FormHelpers/DatePicker";
import { api } from "@/api";
import utils from "@/utils";
import MealPlanCard from "./MealPlanCard";
export default {
  components: {
    MealPlanCard,
    DatePicker,
  },
  data() {
    return {
      isLoading: false,
      meals: [],
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
      this.meals = [];
      for (let i = 0; i < this.dateDif; i++) {
        this.meals.push({
          slug: "empty",
          date: this.getDate(i),
        });
      }
    },
  },
  async mounted() {
    await this.$store.dispatch("requestCurrentGroup");
    await this.buildMealStore();
  },

  computed: {
    groupSettings() {
      return this.$store.getters.getCurrentGroup;
    },
    actualStartDate() {
      return Date.parse(this.startDate);
    },
    actualEndDate() {
      return Date.parse(this.endDate);
    },
    dateDif() {
      let startDate = new Date(this.startDate);
      let endDate = new Date(this.endDate);

      let dateDif = (endDate - startDate) / (1000 * 3600 * 24) + 1;

      if (dateDif < 1) {
        return null;
      }

      return dateDif;
    },
    startComputedDateFormatted() {
      return this.formatDate(this.startDate);
    },
    endComputedDateFormatted() {
      return this.formatDate(this.endDate);
    },
    filteredRecipes() {
      const recipes = this.items.filter(x => !this.usedRecipes.includes(x));
      return recipes.length > 0 ? recipes : this.items;
    },
  },

  methods: {
    async buildMealStore() {
      const categories = Array.from(this.groupSettings.categories, x => x.name);
      this.items = await api.recipes.getAllByCategory(categories);

      if (this.items.length === 0) {
        const keys = [
          "name",
          "slug",
          "image",
          "description",
          "dateAdded",
          "rating",
        ];
        this.items = await api.recipes.allByKeys(keys);
      }
    },
    getRandom(list) {
      let recipe = 1;
      while (this.usedRecipes.includes(recipe)) {
        recipe = list[Math.floor(Math.random() * list.length)];
      }
      return recipe;
    },
    random() {
      this.usedRecipes = [1];
      this.meals.forEach((element, index) => {
        let recipe = this.getRandom(this.filteredRecipes);
        this.meals[index]["slug"] = recipe.slug;
        this.meals[index]["name"] = recipe.name;
        this.usedRecipes.push(recipe);
      });
    },
    processTime(index) {
      let dateText = new Date(
        this.actualStartDate.valueOf() + 1000 * 3600 * 24 * index
      );
      return dateText;
    },
    getDate(index) {
      const dateObj = this.processTime(index);
      return utils.getDateAsPythonDate(dateObj);
    },

    async save() {
      const mealBody = {
        group: this.groupSettings.name,
        startDate: this.startDate,
        endDate: this.endDate,
        meals: this.meals,
      };
      await api.mealPlans.create(mealBody);
      this.$emit(CREATE_EVENT);
      this.meals = [];
      this.startDate = null;
      this.endDate = null;
    },

    getImage(image) {
      return api.recipes.recipeSmallImage(image);
    },

    formatDate(date) {
      if (!date) return null;

      const [year, month, day] = date.split("-");
      return `${month}/${day}/${year}`;
    },
    parseDate(date) {
      if (!date) return null;

      const [month, day, year] = date.split("/");
      return `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`;
    },
    getNextDayOfTheWeek(dayName, excludeToday = true, refDate = new Date()) {
      const dayOfWeek = [
        "sun",
        "mon",
        "tue",
        "wed",
        "thu",
        "fri",
        "sat",
      ].indexOf(dayName.slice(0, 3).toLowerCase());
      if (dayOfWeek < 0) return;
      refDate.setHours(0, 0, 0, 0);
      refDate.setDate(
        refDate.getDate() +
          +!!excludeToday +
          ((dayOfWeek + 7 - refDate.getDay() - +!!excludeToday) % 7)
      );
      return refDate;
    },
    setQuickWeek() {
      const nextMonday = this.getNextDayOfTheWeek("Monday", false);
      const nextEndDate = new Date(nextMonday);
      nextEndDate.setDate(nextEndDate.getDate() + 4);

      this.startDate = nextMonday.toISOString().substr(0, 10);
      this.endDate = nextEndDate.toISOString().substr(0, 10);
    },
  },
};
</script>

<style>
</style>