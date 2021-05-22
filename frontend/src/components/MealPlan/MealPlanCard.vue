<template>
  <v-row>
    <SearchDialog ref="mealselect" @select="setSlug" />
    <v-col cols="12" sm="12" md="6" lg="4" xl="3" v-for="(planDay, index) in value" :key="index">
      <v-hover v-slot="{ hover }" :open-delay="50">
        <v-card :class="{ 'on-hover': hover }" :elevation="hover ? 12 : 2">
          <CardImage large :slug="planDay.meals[0].slug" icon-size="200" @click="openSearch(index, modes.primary)">
          </CardImage>

          <v-card-title class="my-n3 mb-n6">
            {{ $d(new Date(planDay.date.split("-")), "short") }}
          </v-card-title>
          <v-card-subtitle class="mb-0 pb-0"> {{ planDay.meals[0].name }}</v-card-subtitle>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="info" outlined small @click="openSearch(index, modes.sides)">
              <v-icon small class="mr-1">
                mdi-plus
              </v-icon>
              Side
            </v-btn>
          </v-card-actions>
          <v-divider class="mx-2"></v-divider>
          <v-list dense>
            <v-list-item v-for="(recipe, i) in planDay.meals.slice(1)" :key="i">
              <v-list-item-avatar>
                <v-img :alt="recipe.slug" :src="getImage(recipe.slug)"></v-img>
              </v-list-item-avatar>

              <v-list-item-content>
                <v-list-item-title v-text="recipe.name"></v-list-item-title>
              </v-list-item-content>

              <v-list-item-icon>
                <v-btn icon @click="removeSide(index, i + 1)">
                  <v-icon color="error">
                    mdi-delete
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
import SearchDialog from "../UI/Search/SearchDialog";
import { api } from "@/api";
import CardImage from "../Recipe/CardImage.vue";
export default {
  components: {
    SearchDialog,
    CardImage,
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
    };
  },
  watch: {
    value(val) {
      console.log(val);
    },
  },
  mounted() {
    console.log(this.value);
  },
  methods: {
    getImage(slug) {
      if (slug) {
        return api.recipes.recipeSmallImage(slug);
      }
    },
    setSide(name, slug) {
      const meal = { name: name, slug: slug };
      this.value[this.activeIndex]["meals"].push(meal);
    },
    setPrimary(name, slug) {
      this.value[this.activeIndex]["meals"][0]["slug"] = slug;
      this.value[this.activeIndex]["meals"][0]["name"] = name;
    },
    setSlug(name, slug) {
      switch (this.mode) {
        case this.modes.primary:
          this.setPrimary(name, slug);
          break;
        default:
          this.setSide(name, slug);
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
  },
};
</script>

<style>
.relative-card {
  position: relative;
}
</style>
