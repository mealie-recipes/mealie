<template>
  <v-row>
    <SearchDialog ref="mealselect" @selected="setSlug" />
    <BaseDialog
      title="Custom Meal"
      :title-icon="$globals.icons.primary"
      submit-text="Save"
      :top="true"
      ref="customMealDialog"
      @submit="pushCustomMeal"
    >
      <v-card-text>
        <v-text-field autofocus v-model="customMeal.name" label="Name"> </v-text-field>
        <v-textarea v-model="customMeal.description" label="Description"> </v-textarea>
      </v-card-text>
    </BaseDialog>
    <v-col cols="12" sm="12" md="6" lg="4" xl="3" v-for="(planDay, index) in value" :key="index">
      <v-hover v-slot="{ hover }" :open-delay="50">
        <v-card :class="{ 'on-hover': hover }" :elevation="hover ? 12 : 2">
          <CardImage large :slug="planDay.meals[0].slug" icon-size="200" @click="openSearch(index, modes.primary)">
            <v-fade-transition>
              <v-btn v-if="hover" small color="info" class="ma-1" @click.stop="addCustomItem(index, modes.primary)">
                <v-icon left>
                  {{ $globals.icons.edit }}
                </v-icon>
                No Recipe
              </v-btn>
            </v-fade-transition>
          </CardImage>

          <v-card-title class="my-n3 mb-n6">
            {{ $d(new Date(planDay.date.split("-")), "short") }}
          </v-card-title>
          <v-card-subtitle class="mb-0 pb-0"> {{ planDay.meals[0].name }}</v-card-subtitle>
          <v-hover v-slot="{ hover }">
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-fade-transition>
                <v-btn v-if="hover" small color="info" text @click.stop="addCustomItem(index, modes.sides)">
                  <v-icon left>
                    {{ $globals.icons.edit }}
                  </v-icon>
                  No Recipe
                </v-btn>
              </v-fade-transition>
              <v-btn color="info" outlined small @click="openSearch(index, modes.sides)">
                <v-icon small class="mr-1">
                  {{ $globals.icons.create }}
                </v-icon>
                Side
              </v-btn>
            </v-card-actions>
          </v-hover>
          <v-divider class="mx-2"></v-divider>
          <v-list dense>
            <v-list-item v-for="(recipe, i) in planDay.meals.slice(1)" :key="i">
              <v-list-item-avatar color="accent">
                <v-img :alt="recipe.slug" :src="getImage(recipe.slug)"></v-img>
              </v-list-item-avatar>

              <v-list-item-content>
                <v-list-item-title v-text="recipe.name"></v-list-item-title>
              </v-list-item-content>

              <v-list-item-icon>
                <v-btn icon @click="removeSide(index, i + 1)">
                  <v-icon color="error">
                    {{ $globals.icons.delete }}
                  </v-icon>
                </v-btn>
              </v-list-item-icon>
            </v-list-item>
          </v-list>
        </v-card>
      </v-hover>
    </v-col>
  </v-row>
</template>

<script>
import SearchDialog from "../UI/Dialogs/SearchDialog";
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import { api } from "@/api";
import CardImage from "../Recipe/CardImage.vue";
export default {
  components: {
    SearchDialog,
    CardImage,
    BaseDialog,
  },
  props: {
    value: Array,
  },
  data() {
    return {
      activeIndex: 0,
      mode: "PRIMARY",
      modes: {
        primary: "PRIMARY",
        sides: "SIDES",
      },
      customMeal: {
        slug: null,
        name: "",
        description: "",
      },
    };
  },

  methods: {
    getImage(slug) {
      if (slug) {
        return api.recipes.recipeSmallImage(slug);
      }
    },
    setSide(name, slug = null, description = "") {
      const meal = { name: name, slug: slug, description: description };
      this.value[this.activeIndex]["meals"].push(meal);
    },
    setPrimary(name, slug, description = "") {
      this.value[this.activeIndex]["meals"][0]["slug"] = slug;
      this.value[this.activeIndex]["meals"][0]["name"] = name;
      this.value[this.activeIndex]["meals"][0]["description"] = description;
    },
    setSlug(recipe) {
      switch (this.mode) {
        case this.modes.primary:
          this.setPrimary(recipe.name, recipe.slug);
          break;
        default:
          this.setSide(recipe.name, recipe.slug);
          break;
      }
    },
    openSearch(index, mode) {
      this.mode = mode;
      this.activeIndex = index;
      this.$refs.mealselect.open();
    },
    removeSide(dayIndex, sideIndex) {
      this.value[dayIndex]["meals"].splice(sideIndex, 1);
    },
    addCustomItem(index, mode) {
      this.mode = mode;
      this.activeIndex = index;
      this.$refs.customMealDialog.open();
    },
    pushCustomMeal() {
      switch (this.mode) {
        case this.modes.primary:
          this.setPrimary(this.customMeal.name, this.customMeal.slug, this.customMeal.description);
          break;
        default:
          this.setSide(this.customMeal.name, this.customMeal.slug, this.customMeal.description);
          break;
      }
      this.customMeal = { name: "", slug: null, description: "" };
    },
  },
};
</script>

<style>
.relative-card {
  position: relative;
}

.custom-button {
  z-index: -1;
}
</style>
