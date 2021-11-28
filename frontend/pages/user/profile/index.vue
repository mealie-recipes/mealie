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
      <v-card v-if="$auth.user.canInvite" flat color="background" width="100%" max-width="600px">
        <v-card-actions class="d-flex justify-center">
          <v-btn outlined rounded @click="getSignupLink()">
            <v-icon left>
              {{ $globals.icons.createAlt }}
            </v-icon>
            Get Invite Link
          </v-btn>
        </v-card-actions>
        <div v-show="generatedLink !== ''">
          <v-card-text>
            <p class="text-center pb-0">
              {{ generatedLink }}
            </p>
            <v-text-field v-model="sendTo" :label="$t('user.email')" :rules="[validators.email]"> </v-text-field>
          </v-card-text>
          <v-card-actions class="py-0 align-center" style="gap: 4px">
            <BaseButton cancel @click="generatedLink = ''"> {{ $t("general.close") }} </BaseButton>
            <v-spacer></v-spacer>
            <AppButtonCopy :icon="false" color="info" :copy-text="generatedLink" />
            <BaseButton color="info" :disabled="!validEmail" :loading="loading" @click="sendInvite">
              <template #icon>
                {{ $globals.icons.email }}
              </template>
              {{ $t("user.email") }}
            </BaseButton>
          </v-card-actions>
        </div>
      </v-card>
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
        <v-col v-if="user.advanced" cols="12" sm="12" md="6">
          <UserProfileLinkCard
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
        <v-col v-if="user.advanced" cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Manage Webhooks', to: '/user/group/webhooks' }"
            :image="require('~/static/svgs/manage-webhooks.svg')"
          >
            <template #title> Webhooks </template>
            Setup webhooks that trigger on days that you have have mealplan scheduled.
          </UserProfileLinkCard>
        </v-col>
        <v-col v-if="user.canManage" cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Manage Members', to: '/user/group/members' }"
            :image="require('~/static/svgs/manage-members.svg')"
          >
            <template #title> Members </template>
            See who's in your group and manage their permissions.
          </UserProfileLinkCard>
        </v-col>
        <v-col v-if="user.advanced" cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Manage Recipe Data', to: '/user/group/data/recipes' }"
            :image="require('~/static/svgs/manage-recipes.svg')"
          >
            <template #title> Recipe Data </template>
            Manage your recipe data and make bulk changes
          </UserProfileLinkCard>
        </v-col>
        <v-col v-if="user.advanced" cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Manage Data Migrations', to: '/user/group/data/migrations' }"
            :image="require('~/static/svgs/manage-data-migrations.svg')"
          >
            <template #title> Data Migrations </template>
            Migrate your existing data from other applications like Nextcloud Recipes and Chowdown
          </UserProfileLinkCard>
        </v-col>
      </v-row>
    </section>
  </v-container>
</template>
    
<script lang="ts">
import { computed, defineComponent, useContext, ref, toRefs, reactive } from "@nuxtjs/composition-api";
import UserProfileLinkCard from "@/components/Domain/User/UserProfileLinkCard.vue";
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { alert } from "~/composables/use-toast";

export default defineComponent({
  components: {
    UserProfileLinkCard,
  },
  scrollToTop: true,
  setup() {
    const { $auth } = useContext();

    const user = computed(() => $auth.user);

    const generatedLink = ref("");
    const token = ref("");
    const api = useUserApi();
    async function getSignupLink() {
      const { data } = await api.groups.createInvitation({ uses: 1 });
      if (data) {
        token.value = data.token;
        generatedLink.value = constructLink(data.token);
      }
    }

    function constructLink(token: string) {
      return `${window.location.origin}/register?token=${token}`;
    }

    // =================================================
    // Email Invitation
    const state = reactive({
      loading: false,
      sendTo: "",
    });

    async function sendInvite() {
      state.loading = true;
      const { data } = await api.email.sendInvitation({
        email: state.sendTo,
        token: token.value,
      });

      if (data && data.success) {
        alert.success("Email Sent");
      } else {
        alert.error("Error Sending Email");
      }
      state.loading = false;
    }

    const validEmail = computed(() => {
      if (state.sendTo === "") {
        return false;
      }
      const valid = validators.email(state.sendTo);

      // Explicit bool check because validators.email sometimes returns a string
      if (valid === true) {
        return true;
      }
      return false;
    });

    return {
      user,
      constructLink,
      generatedLink,
      getSignupLink,
      sendInvite,
      validators,
      validEmail,
      ...toRefs(state),
    };
  },
  head() {
    return {
      title: this.$t("settings.profile") as string,
    };
  },
});
</script>
    
