<template>
  <v-container v-if="user">
    <section class="d-flex flex-column align-center">
      <v-avatar color="primary" size="75" class="mb-2">
        <v-img :src="require(`~/static/account.png`)" />
      </v-avatar>
      <h2 class="headline">👋 Welcome, {{ user.fullName }}</h2>
      <p class="subtitle-1 mb-0">
        Manage your profile, recipes, and group settings.
        <a href="https://hay-kot.github.io/mealie/" target="_blank"> Learn More </a>
      </p>
    </section>
    <section>
      <div>
        <h3 class="headline">Personal</h3>
        <p>These are settings that are personal to you. Changes here won't affect other users</p>
      </div>
      <v-row tag="section">
        <v-col cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Manage User Profile', to: '/user/profile/edit' }"
            :image="require('~/static/svgs/manage-profile.svg')"
          >
            <template #title> User Settings </template>
            Manage your preferences, change your password, and update your email
          </UserProfileLinkCard>
        </v-col>
        <v-col cols="12" sm="12" md="6">
          <UserProfileLinkCard
            v-if="user.advanced"
            :link="{ text: 'Manage Your API Tokens', to: '/user/profile/api-tokens' }"
            :image="require('~/static/svgs/manage-api-tokens.svg')"
          >
            <template #title> API Tokens </template>
            Manage your API Tokens for access from external applications
          </UserProfileLinkCard>
        </v-col>
      </v-row>
    </section>
    <v-divider class="my-7"></v-divider>
    <section>
      <div>
        <h3 class="headline">Group</h3>
        <p>These items are shared within your group. Editing one of them will change it for the whole group!</p>
      </div>
      <v-row tag="section">
        <v-col cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Group Settings', to: '/user/group' }"
            :image="require('~/static/svgs/manage-group-settings.svg')"
          >
            <template #title> Group Settings </template>
            Manage your common group settings like mealplan and privacy settings.
          </UserProfileLinkCard>
        </v-col>
        <v-col cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Manage Cookbooks', to: '/user/group/cookbooks' }"
            :image="require('~/static/svgs/manage-cookbooks.svg')"
          >
            <template #title> Cookbooks </template>
            Manage a collection of recipe categories and generate pages for them.
          </UserProfileLinkCard>
        </v-col>
        <v-col cols="12" sm="12" md="6">
          <UserProfileLinkCard
            v-if="user.advanced"
            :link="{ text: 'Manage Webhooks', to: '/user/group/webhooks' }"
            :image="require('~/static/svgs/manage-webhooks.svg')"
          >
            <template #title> Webhooks </template>
            Setup webhooks that trigger on days that you have have mealplan scheduled.
          </UserProfileLinkCard>
        </v-col>
      </v-row>
    </section>
  </v-container>
</template>
    
<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import UserProfileLinkCard from "@/components/Domain/User/UserProfileLinkCard.vue";

export default defineComponent({
  components: {
    UserProfileLinkCard,
  },
  setup() {
    const user = computed(() => useContext().$auth.user);

    return { user };
  },
});
</script>
    
