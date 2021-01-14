<template>
  <v-card>
    <v-card-title class="headline">
      {{$t('meal-plan.create-a-new-meal-plan')}}
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
            <v-date-picker
              v-model="startDate"
              no-title
              @input="menu2 = false"
            ></v-date-picker>
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
            <v-date-picker
              v-model="endDate"
              no-title
              @input="menu2 = false"
            ></v-date-picker>
          </v-menu>
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-text>
      <MealPlanCard v-model="meals" />
    </v-card-text>
    <v-row align="center" justify="end">
      <v-card-actions>
        <v-btn color="success" @click="random" v-if="meals[1]" text>
          {{$t('general.random')}}
        </v-btn>
        <v-btn color="success" @click="save" text> {{$t('general.save')}} </v-btn>

        <v-spacer></v-spacer>
        <v-btn icon @click="show = !show"> </v-btn>
      </v-card-actions>
    </v-row>
  </v-card>
</template>

<script>
import api from "../../api";
import utils from "../../utils";
import MealPlanCard from "./MealPlanCard";
export default {
  components: {
    MealPlanCard,
  },
  data() {
    return {
      isLoading: false,
      meals: [],

      // Dates
      startDate: null,
      endDate: null,
      menu1: false,
      menu2: false,
    };
  },

  watch: {
    dateDif() {
      this.meals = [];
      for (let i = 0; i < this.dateDif; i++) {
        this.meals.push({
          slug: "empty",
          date: this.getDate(i),
          dateText: this.getDayText(i),
        });
      }
    },
  },

  computed: {
    items() {
      return this.$store.getters.getRecentRecipes;
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

      if (dateDif <= 1) {
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
  },

  methods: {
    get_random(list) {
      const object = list[Math.floor(Math.random() * list.length)];
      return object.slug;
    },
    random() {
      this.meals.forEach((element, index) => {
        this.meals[index]["slug"] = this.get_random(this.items);
      });
    },
    processTime(index) {
      let dateText = new Date(
        this.actualStartDate.valueOf() + 1000 * 3600 * 24 * index
      );
      return dateText;
    },
    getDayText(index) {
      const dateObj = this.processTime(index);
      return utils.getDateAsText(dateObj);
    },
    getDate(index) {
      const dateObj = this.processTime(index);
      return utils.getDateAsPythonDate(dateObj);
    },

    async save() {
      const mealBody = {
        startDate: this.startDate,
        endDate: this.endDate,
        meals: this.meals,
      };
      await api.mealPlans.create(mealBody);
      this.$emit("created");
      this.startDate = null;
      this.endDate = null;
      this.meals = [];
    },

    getImage(image) {
      return utils.getImageURL(image);
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
  },
};
</script>

<style>
</style>