<template>
  <div>
    <v-card-title class="headline">
      {{ name }}
    </v-card-title>
    <v-card-text>
      {{ description }}
      <div class="my-2"></div>
      <v-row dense disabled>
        <v-col>
          <v-btn
            v-if="yields"
            dense
            small
            :hover="false"
            type="label"
            :ripple="false"
            elevation="0"
            color="secondary darken-1"
            class="rounded-sm static"
          >
            {{ yields }}
          </v-btn>
        </v-col>
        <v-rating
          class="mr-2 align-end static"
          color="secondary darken-1"
          background-color="secondary lighten-3"
          length="5"
          :value="rating"
        ></v-rating>
      </v-row>
      <v-row>
        <v-col cols="12" sm="12" md="4" lg="4">
          <h2 class="mb-4">{{$t('recipe.ingredients')}}</h2>
          <div
            v-for="(ingredient, index) in ingredients"
            :key="generateKey('ingredient', index)"
          >
            <v-checkbox
              hide-details
              class="ingredients"
              :label="ingredient"
              color="secondary"
            >
            </v-checkbox>
          </div>

          <div v-if="categories[0]">
            <h2 class="mt-4">{{$t('recipe.categories')}}</h2>
            <v-chip
              class="ma-1"
              color="primary"
              dark
              v-for="category in categories"
              :key="category"
            >
              {{ category }}
            </v-chip>
          </div>

          <div v-if="tags[0]">
            <h2 class="mt-4">{{$t('recipe.tags')}}</h2>
            <v-chip
              class="ma-1"
              color="primary"
              dark
              v-for="tag in tags"
              :key="tag"
            >
              {{ tag }}
            </v-chip>
          </div>

          <h2 v-if="notes[0]" class="my-4">{{$t('recipe.notes')}}</h2>
          <v-card
            class="mt-1"
            v-for="(note, index) in notes"
            :key="generateKey('note', index)"
          >
            <v-card-title> {{ note.title }}</v-card-title>
            <v-card-text>
              {{ note.text }}
            </v-card-text>
          </v-card>
        </v-col>
        <v-divider class="my-divider" :vertical="true"></v-divider>

        <v-col cols="12" sm="12" md="8" lg="8">
          <h2 class="mb-4">{{$t('recipe.instructions')}}</h2>
          <v-hover
            v-for="(step, index) in instructions"
            :key="generateKey('step', index)"
            v-slot="{ hover }"
          >
            <v-card
              class="ma-1"
              :class="[{ 'on-hover': hover }, isDisabled(index)]"
              :elevation="hover ? 12 : 2"
              @click="toggleDisabled(index)"
            >
              <v-card-title>{{ $t('recipe.step-index', {step: index + 1}) }}</v-card-title>
              <v-card-text>{{ step.text }}</v-card-text>
            </v-card>
          </v-hover>
        </v-col>
      </v-row>
      <v-row>
        <v-col></v-col>

        <v-btn
          v-if="orgURL"
          dense
          small
          :hover="false"
          type="label"
          :ripple="false"
          elevation="0"
          :href="orgURL"
          color="secondary darken-1"
          target="_blank"
          class="rounded-sm mr-4"
        >
          {{$t('recipe.original-recipe')}}
        </v-btn>
      </v-row>
    </v-card-text>
  </div>
</template>

<script>
import utils from "../../utils";
export default {
  props: {
    name: String,
    description: String,
    ingredients: Array,
    instructions: Array,
    categories: Array,
    tags: Array,
    notes: Array,
    rating: Number,
    yields: String,
    orgURL: String,
  },
  data() {
    return {
      disabledSteps: [],
    };
  },
  methods: {
    toggleDisabled(stepIndex) {
      if (this.disabledSteps.includes(stepIndex)) {
        let index = this.disabledSteps.indexOf(stepIndex);
        if (index !== -1) {
          this.disabledSteps.splice(index, 1);
        }
      } else {
        this.disabledSteps.push(stepIndex);
      }
    },
    isDisabled(stepIndex) {
      if (this.disabledSteps.includes(stepIndex)) {
        return "disabled-card";
      } else {
        return;
      }
    },
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
  },
};
</script>

<style>
.static {
  pointer-events: none;
}
.my-divider {
  margin: 0 -1px;
}
</style>