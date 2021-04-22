<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="650">
      <v-card>
        <v-card-title class="headline">
          {{$t('meal-plan.shopping-list')}}
          <v-spacer></v-spacer>
          <v-btn text color="accent" @click="group = !group">
            {{$t('meal-plan.group')}}
          </v-btn>
        </v-card-title>
        <v-divider></v-divider>

        <v-card-text v-if="group == false">
          <v-list
            dense
            v-for="(recipe, index) in ingredients"
            :key="`${index}-recipe`"
          >
            <v-subheader>{{ recipe.name }} </v-subheader>
            <v-divider></v-divider>

            <v-list-item-group color="primary">
              <v-list-item
                v-for="(item, i) in recipe.recipeIngredient"
                :key="i"
              >
                <v-list-item-content>
                  <v-list-item-title v-text="item"></v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-card-text>

        <v-card-text v-else>
          <v-list dense>
            <v-list-item-group color="primary">
              <v-list-item v-for="(item, i) in rawIngredients" :key="i">
                <v-list-item-content>
                  <v-list-item-title v-text="item"></v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-card-text>

        <v-divider></v-divider>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { api } from "@/api";
const levenshtein = require("fast-levenshtein");
export default {
  data() {
    return {
      dialog: false,
      planID: 0,
      ingredients: [],
      rawIngredients: [],
      group: false,
    };
  },
  methods: {
    openDialog: function(id) {
      this.dialog = true;
      this.planID = id;
      this.getIngredients();
    },
    async getIngredients() {
      this.ingredients = await api.mealPlans.shoppingList(this.planID);
      this.getRawIngredients();
    },
    getRawIngredients() {
      this.ingredients.forEach(element => {
        this.rawIngredients.push(element.recipeIngredient);
      });

      this.rawIngredients = this.rawIngredients.flat();
      this.rawIngredients = this.levenshteinFilter(this.rawIngredients);
    },
    levenshteinFilter(source, maximum = 5) {
      let _source, matches, x, y;
      _source = source.slice();
      matches = [];
      for (x = _source.length - 1; x >= 0; x--) {
        let output = _source.splice(x, 1);
        for (y = _source.length - 1; y >= 0; y--) {
          if (levenshtein.get(output[0], _source[y]) <= maximum) {
            output.push(_source[y]);
            _source.splice(y, 1);
            x--;
          }
        }
        matches.push(output);
      }
      return matches.flat();
    },
  },
};
</script>




<style>
</style>