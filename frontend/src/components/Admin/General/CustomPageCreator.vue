<template>
  <v-card flat>
    <v-card-text>
      <h2 class="mt-1 mb-1 ">
        Custom Pages
        <span>
          <v-btn color="success" small class="ml-3">
            New
          </v-btn>
        </span>
      </h2>
      <v-row class="mt-1">
        <v-col
          :sm="6"
          :md="6"
          :lg="4"
          :xl="3"
          v-for="item in customPages"
          :key="item + item.id"
        >
          <v-card>
            <v-card-title class="headline">{{ item.name }}</v-card-title>
            <v-divider></v-divider>

            <v-card-text>
              Card Position: {{ item.position }}
              <div>
                <v-chip
                  v-for="cat in item.categories"
                  :key="cat.slug + cat.id"
                  class="my-2 mr-2"
                  label
                  small
                  color="accent lighten-1"
                >
                  {{ cat.name }}
                </v-chip>
              </div>
            </v-card-text>

            <v-card-actions>
              <v-btn text small color="error">
                Delete
              </v-btn>
              <v-spacer> </v-spacer>
              <v-btn small text color="success">
                Edit
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  data() {
    return {
      customPages: [
        {
          id: 0,
          name: "My Page Name",
          slug: "my-page-name",
          position: 0,
          categories: [
            {
              id: 2,
              slug: "brownie",
              name: "brownie",
            },
            {
              id: 3,
              slug: "dessert",
              name: "dessert",
            },
            {
              id: 4,
              slug: "drink",
              name: "Drink",
            },
          ],
        },
        {
          id: 3,
          name: "My Page Name 1",
          slug: "my-page-name",
          position: 1,
          categories: [
            {
              id: 2,
              slug: "brownie",
              name: "brownie",
            },
            {
              id: 3,
              slug: "dessert",
              name: "dessert",
            },
            {
              id: 4,
              slug: "drink",
              name: "Drink",
            },
          ],
        },
        {
          id: 2,
          name: "My Page Name 2",
          slug: "my-page-name",
          position: 2,
          categories: [
            {
              id: 2,
              slug: "brownie",
              name: "brownie",
            },
            {
              id: 3,
              slug: "dessert",
              name: "dessert",
            },
            {
              id: 4,
              slug: "drink",
              name: "Drink",
            },
          ],
        },
      ],
    };
  },
};
</script>

<style lang="scss" scoped>
</style>