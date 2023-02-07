<template>
  <v-container v-if="user">
    <section class="d-flex flex-column align-center">
      <UserAvatar size="84" :user-id="$auth.user.id" />

      <h2 class="headline">{{ $t('profile.welcome-user', [user.fullName]) }}</h2>
      <p class="subtitle-1 mb-0">
       {{ $t('profile.description') }}
        <a href="https://hay-kot.github.io/mealie/" target="_blank"> {{ $t('general.learn-more') }} </a>
      </p>
      <v-card v-if="$auth.user.canInvite" flat color="background" width="100%" max-width="600px">
        <v-card-actions class="d-flex justify-center">
          <v-btn outlined rounded @click="getSignupLink()">
            <v-icon left>
              {{ $globals.icons.createAlt }}
            </v-icon>
            {{ $t('profile.get-invite-link') }}
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
    <section class="my-3">
      <div>
        <h3 class="headline">{{ $t('profile.account-summary') }}</h3>
        <p>{{ $t('profile.account-summary-description') }}</p>
      </div>
      <v-row tag="section">
        <v-col cols="12" sm="12" md="6">
          <v-card outlined>
            <v-card-title class="headline pb-0"> {{ $t('profile.group-statistics') }} </v-card-title>
            <v-card-text class="py-0">
              {{ $t('profile.group-statistics-description') }}
            </v-card-text>
            <v-card-text class="d-flex flex-wrap justify-center align-center" style="gap: 0.8rem">
              <StatsCards
                v-for="(value, key) in stats"
                :key="`${key}-${value}`"
                :min-width="$vuetify.breakpoint.xs ? '100%' : '158'"
                :icon="getStatsIcon(key)"
                :to="getStatsTo(key)"
              >
                <template #title> {{ getStatsTitle(key) }}</template>
                <template #value> {{ value }}</template>
              </StatsCards>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="12" md="6" class="d-flex align-strart">
          <v-card outlined>
            <v-card-title class="headline pb-0"> {{ $t('profile.storage-capacity') }} </v-card-title>
            <v-card-text class="py-0">
              {{ $t('profile.storage-capacity-description') }}
              <strong> {{ $t('general.this-feature-is-currently-inactive') }}</strong>
            </v-card-text>
            <v-card-text>
              <v-progress-linear :value="storageUsedPercentage" color="accent" class="rounded" height="30">
                <template #default>
                  <strong> {{ storageText }} </strong>
                </template>
              </v-progress-linear>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </section>
    <v-divider class="my-7"></v-divider>
    <section>
      <div>
        <h3 class="headline">{{ $t('profile.personal') }}</h3>
        <p>{{ $t('profile.personal-description') }}</p>
      </div>
      <v-row tag="section">
        <v-col cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Manage User Profile', to: '/user/profile/edit' }"
            :image="require('~/static/svgs/manage-profile.svg')"
          >
            <template #title> {{ $t('profile.user-settings') }} </template>
            {{ $t('profile.user-settings-description') }}
          </UserProfileLinkCard>
        </v-col>
        <AdvancedOnly>
          <v-col cols="12" sm="12" md="6">
            <UserProfileLinkCard
              :link="{ text: 'Manage Your API Tokens', to: '/user/profile/api-tokens' }"
              :image="require('~/static/svgs/manage-api-tokens.svg')"
            >
              <template #title> {{ $t('settings.token.api-tokens') }} </template>
              {{ $t('profile.api-tokens-description') }}
            </UserProfileLinkCard>
          </v-col>
        </AdvancedOnly>
      </v-row>
    </section>
    <v-divider class="my-7"></v-divider>
    <section>
      <div>
        <h3 class="headline">{{ $t('group.group') }}</h3>
        <p>{{ $t('profile.group-description') }}</p>
      </div>
      <v-row tag="section">
        <v-col cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Group Settings', to: '/group' }"
            :image="require('~/static/svgs/manage-group-settings.svg')"
          >
            <template #title> {{ $t('profile.group-settings') }} </template>
            {{ $t('profile.group-settings-description') }}
          </UserProfileLinkCard>
        </v-col>
        <v-col cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Manage Cookbooks', to: '/group/cookbooks' }"
            :image="require('~/static/svgs/manage-cookbooks.svg')"
          >
            <template #title> {{ $t('sidebar.cookbooks') }} </template>
            {{ $t('profile.cookbooks-description') }}
          </UserProfileLinkCard>
        </v-col>
        <v-col v-if="user.canManage" cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: 'Manage Members', to: '/group/members' }"
            :image="require('~/static/svgs/manage-members.svg')"
          >
            <template #title> {{ $t('profile.members') }} </template>
            {{ $t('profile.members-description') }}
          </UserProfileLinkCard>
        </v-col>
        <AdvancedOnly>
          <v-col v-if="user.advanced" cols="12" sm="12" md="6">
            <UserProfileLinkCard
              :link="{ text: 'Manage Webhooks', to: '/group/webhooks' }"
              :image="require('~/static/svgs/manage-webhooks.svg')"
            >
              <template #title> {{ $t('settings.webhooks.webhooks') }} </template>
              {{ $t('profile.webhooks-description') }}
            </UserProfileLinkCard>
          </v-col>
        </AdvancedOnly>
        <AdvancedOnly>
          <v-col cols="12" sm="12" md="6">
            <UserProfileLinkCard
              :link="{ text: 'Manage Notifiers', to: '/group/notifiers' }"
              :image="require('~/static/svgs/manage-notifiers.svg')"
            >
              <template #title> {{ $t('profile.notifiers') }} </template>
              {{ $t('profile.notifiers-description') }}
            </UserProfileLinkCard>
          </v-col>
        </AdvancedOnly>
        <AdvancedOnly>
          <v-col cols="12" sm="12" md="6">
            <UserProfileLinkCard
              :link="{ text: 'Manage Data', to: '/group/data/foods' }"
              :image="require('~/static/svgs/manage-recipes.svg')"
            >
              <template #title> {{ $t('profile.manage-data') }} </template>
              {{ $t('profile.manage-data-description') }}
            </UserProfileLinkCard>
          </v-col>
        </AdvancedOnly>
        <AdvancedOnly>
          <v-col cols="12" sm="12" md="6">
            <UserProfileLinkCard
              :link="{ text: 'Manage Data Migrations', to: '/group/migrations' }"
              :image="require('~/static/svgs/manage-data-migrations.svg')"
            >
              <template #title>{{ $t('profile.data-migrations') }} </template>
              {{ $t('profile.data-migrations-description') }}
            </UserProfileLinkCard>
          </v-col>
        </AdvancedOnly>
      </v-row>
    </section>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, useContext, ref, toRefs, reactive, useAsync } from "@nuxtjs/composition-api";
import UserProfileLinkCard from "@/components/Domain/User/UserProfileLinkCard.vue";
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { alert } from "~/composables/use-toast";
import UserAvatar from "@/components/Domain/User/UserAvatar.vue";
import { useAsyncKey } from "~/composables/use-utils";
import StatsCards from "~/components/global/StatsCards.vue";

export default defineComponent({
  name: "UserProfile",
  components: {
    UserProfileLinkCard,
    UserAvatar,
    StatsCards,
  },
  scrollToTop: true,
  setup() {
    const { $auth, i18n } = useContext();

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
        alert.success(i18n.tc("profile.email-sent"));
      } else {
        alert.error(i18n.tc("profile.error-sending-email"));
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

    const stats = useAsync(async () => {
      const { data } = await api.groups.statistics();

      if (data) {
        return data;
      }
    }, useAsyncKey());

    const statsText: { [key: string]: string } = {
      totalRecipes: i18n.tc("general.recipes"),
      totalUsers: i18n.tc("user.users"),
      totalCategories: i18n.tc("sidebar.categories"),
      totalTags: i18n.tc("sidebar.tags"),
      totalTools: i18n.tc("tool.tools"),
    };

    function getStatsTitle(key: string) {
      return statsText[key] ?? "unknown";
    }

    const { $globals } = useContext();

    const iconText: { [key: string]: string } = {
      totalUsers: $globals.icons.user,
      totalCategories: $globals.icons.tags,
      totalTags: $globals.icons.tags,
      totalTools: $globals.icons.potSteam,
    };

    function getStatsIcon(key: string) {
      return iconText[key] ?? $globals.icons.primary;
    }

    const statsTo: { [key: string]: string } = {
      totalRecipes: "/recipes/all",
      totalUsers: "/group/members",
      totalCategories: "/recipes/categories",
      totalTags: "/recipes/tags",
      totalTools: "/recipes/tools",
    };

    function getStatsTo(key: string) {
      return statsTo[key] ?? "unknown";
    }

    const storage = useAsync(async () => {
      const { data } = await api.groups.storage();

      if (data) {
        return data;
      }
    }, useAsyncKey());

    const storageUsedPercentage = computed(() => {
      if (!storage.value) {
        return 0;
      }

      return (storage.value?.usedStorageBytes / storage.value?.totalStorageBytes) * 100 ?? 0;
    });

    const storageText = computed(() => {
      if (!storage.value) {
        return "Loading...";
      }
      return `${storage.value.usedStorageStr} / ${storage.value.totalStorageStr}`;
    });

    return {
      storageText,
      storageUsedPercentage,
      getStatsTitle,
      getStatsIcon,
      getStatsTo,
      stats,
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
