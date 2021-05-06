<template>
  <StatCard icon="mdi-account-group">
    <template v-slot:after-heading>
      <div class="ml-auto text-right">
        <div class="body-3 grey--text font-weight-light" v-text="$t('group.group')" />

        <h3 class="display-2 font-weight-light text--primary">
          <small> {{ currentGroup.name }} </small>
        </h3>
      </div>
    </template>
    <template v-slot:bottom>
      <div v-if="todaysMeal">
        <v-subheader>DINNER TONIGHT</v-subheader>
        <MobileRecipeCard
          :name="todaysMeal.name"
          :slug="todaysMeal.slug"
          :description="todaysMeal.description"
          :rating="todaysMeal.rating"
          :tags="true"
        />
      </div>

      <v-subheader>USERS</v-subheader>
      <v-divider></v-divider>

      <v-virtual-scroll v-if="currentGroup.users" :items="currentGroup.users" height="260" item-height="64">
        <template v-slot:default="{ item }">
          <v-list-item :key="item.id">
            <v-list-item-action>
              <v-btn fab small depressed color="primary">
                {{ generateInitials(item.fullName) }}
              </v-btn>
            </v-list-item-action>

            <v-list-item-content>
              <v-list-item-title>
                {{ item.fullName }}
              </v-list-item-title>
            </v-list-item-content>
            <!-- TODO: Future Profile Pages-->
            <!-- <v-list-item-action>
              <v-icon small>
                mdi-open-in-new
              </v-icon>
            </v-list-item-action> -->
          </v-list-item>

          <v-divider></v-divider>
        </template>
      </v-virtual-scroll>
    </template>
  </StatCard>
</template>

<script>
import StatCard from "@/components/UI/StatCard";
import MobileRecipeCard from "@/components/Recipe/MobileRecipeCard";
import { validators } from "@/mixins/validators";
import { initials } from "@/mixins/initials";
import { api } from "@/api";
export default {
  components: {
    StatCard,
    MobileRecipeCard,
  },
  mixins: [validators, initials],
  data() {
    return {
      todaysMeal: false,
      hideImage: false,
      passwordLoading: false,
      password: {
        current: "",
        newOne: "",
        newTwo: "",
      },
      showPassword: false,
      loading: false,
      user: {
        fullName: "",
        email: "",
        group: "",
        admin: false,
        id: 0,
      },
    };
  },

  computed: {
    userProfileImage() {
      this.resetImage();
      return `api/users/${this.user.id}/image`;
    },
    currentGroup() {
      return this.$store.getters.getCurrentGroup;
    },
  },

  mounted() {
    this.getTodaysMeal();
  },

  methods: {
    async getTodaysMeal() {
      const response = await api.mealPlans.today();
      this.todaysMeal = response.data;
    },
    generateInitials(text) {
      const allNames = text.trim().split(" ");
      return allNames.reduce(
        (acc, curr, index) => {
          if (index === 0 || index === allNames.length - 1) {
            acc = `${acc}${curr.charAt(0).toUpperCase()}`;
          }
          return acc;
        },
        [""]
      );
    },
  },
};
</script>

<style></style>
