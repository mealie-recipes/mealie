<template>
  <v-container v-if="user">
    <section class="d-flex flex-column align-center mt-4">
      <UserAvatar :tooltip="false" size="96" :user-id="user.id" />

      <h2 class="headline">{{ $t('profile.welcome-user', [user.fullName]) }}</h2>
      <p class="subtitle-1 mb-0 text-center">
       {{ $t('profile.description') }}
      </p>
      <v-card flat color="transparent" width="100%" max-width="600px">
        <v-card-actions class="d-flex justify-center my-4">
          <v-btn v-if="user.canInvite" outlined rounded @click="inviteDialog = true">
            <v-icon left>
              {{ $globals.icons.createAlt }}
            </v-icon>
            {{ $t('profile.get-invite-link') }}
          </v-btn>
        </v-card-actions>
        <UserInviteDialog v-model="inviteDialog" />
      </v-card>
    </section>
    <section class="my-3">
      <div>
        <h3 class="headline">{{ $t('profile.account-summary') }}</h3>
        <p>{{ $t('profile.account-summary-description') }}</p>
      </div>
      <v-row tag="section">
        <v-col cols="12" sm="12" md="12">
          <v-card outlined>
            <v-card-title class="headline pb-0"> {{ $t('profile.household-statistics') }} </v-card-title>
            <v-card-text class="py-0">
              {{ $t('profile.household-statistics-description') }}
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
            :link="{ text: $tc('profile.manage-user-profile'), to: `/user/profile/edit` }"
            :image="require('~/static/svgs/manage-profile.svg')"
          >
            <template #title> {{ $t('profile.user-settings') }} </template>
            {{ $t('profile.user-settings-description') }}
          </UserProfileLinkCard>
        </v-col>
        <AdvancedOnly>
          <v-col cols="12" sm="12" md="6">
            <UserProfileLinkCard
              :link="{ text: $tc('profile.manage-your-api-tokens'), to: `/user/profile/api-tokens` }"
              :image="require('~/static/svgs/manage-api-tokens.svg')"
            >
              <template #title> {{ $t('settings.token.api-tokens') }} </template>
              {{ $t('profile.api-tokens-description') }}
            </UserProfileLinkCard>
          </v-col>
        </AdvancedOnly>
      </v-row>
    </section>
    <v-divider class="my-7" />
    <section>
      <div>
        <h3 class="headline">{{ $t('household.household') }}</h3>
        <p>{{ $t('profile.household-description') }}</p>
      </div>
      <v-row tag="section">
        <v-col v-if="user.canManageHousehold" cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: $tc('profile.household-settings'), to: `/household` }"
            :image="require('~/static/svgs/manage-group-settings.svg')"
          >
            <template #title> {{ $t('profile.household-settings') }} </template>
            {{ $t('profile.household-settings-description') }}
          </UserProfileLinkCard>
        </v-col>
        <v-col cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: $tc('profile.manage-cookbooks'), to: `/g/${groupSlug}/cookbooks` }"
            :image="require('~/static/svgs/manage-cookbooks.svg')"
          >
            <template #title> {{ $t('sidebar.cookbooks') }} </template>
            {{ $t('profile.cookbooks-description') }}
          </UserProfileLinkCard>
        </v-col>
        <v-col v-if="user.canManage" cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: $tc('profile.manage-members'), to: `/household/members` }"
            :image="require('~/static/svgs/manage-members.svg')"
          >
            <template #title> {{ $t('profile.members') }} </template>
            {{ $t('profile.members-description') }}
          </UserProfileLinkCard>
        </v-col>
        <AdvancedOnly>
          <v-col v-if="user.advanced" cols="12" sm="12" md="6">
            <UserProfileLinkCard
              :link="{ text: $tc('profile.manage-webhooks'), to: `/household/webhooks` }"
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
              :link="{ text: $tc('profile.manage-notifiers'), to: `/household/notifiers` }"
              :image="require('~/static/svgs/manage-notifiers.svg')"
            >
              <template #title> {{ $t('profile.notifiers') }} </template>
              {{ $t('profile.notifiers-description') }}
            </UserProfileLinkCard>
          </v-col>
        </AdvancedOnly>
      </v-row>
    </section>
    <v-divider class="my-7" />
    <section v-if="user.canManage || user.canOrganize || user.advanced">
      <div>
        <h3 class="headline">{{ $t('group.group') }}</h3>
        <p>{{ $t('profile.group-description') }}</p>
      </div>
      <v-row tag="section">
        <v-col v-if="user.canManage" cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: $tc('profile.group-settings'), to: `/group` }"
            :image="require('~/static/svgs/manage-group-settings.svg')"
          >
            <template #title> {{ $t('profile.group-settings') }} </template>
            {{ $t('profile.group-settings-description') }}
          </UserProfileLinkCard>
        </v-col>
        <v-col v-if="user.canOrganize" cols="12" sm="12" md="6">
          <UserProfileLinkCard
            :link="{ text: $tc('profile.manage-data'), to: `/group/data/foods` }"
            :image="require('~/static/svgs/manage-recipes.svg')"
          >
            <template #title> {{ $t('profile.manage-data') }} </template>
            {{ $t('profile.manage-data-description') }}
          </UserProfileLinkCard>
        </v-col>
        <AdvancedOnly>
          <v-col cols="12" sm="12" md="6">
            <UserProfileLinkCard
              :link="{ text: $tc('profile.manage-data-migrations'), to: `/group/migrations` }"
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
import { computed, defineComponent, useContext, ref, useAsync, useRoute } from "@nuxtjs/composition-api";
import UserProfileLinkCard from "@/components/Domain/User/UserProfileLinkCard.vue";
import { useUserApi } from "~/composables/api";
import UserAvatar from "@/components/Domain/User/UserAvatar.vue";
import { useAsyncKey } from "~/composables/use-utils";
import StatsCards from "~/components/global/StatsCards.vue";
import { UserOut } from "~/lib/api/types/user";
import UserInviteDialog from "~/components/Domain/User/UserInviteDialog.vue";

export default defineComponent({
  name: "UserProfile",
  components: {
    UserInviteDialog,
    UserProfileLinkCard,
    UserAvatar,
    StatsCards,
  },
  middleware: "auth",
  scrollToTop: true,
  setup() {
    const { $auth, i18n } = useContext();
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

    // @ts-ignore $auth.user is typed as unknown, but it's a user
    const user = computed<UserOut | null>(() => $auth.user);

    const inviteDialog = ref(false);
    const api = useUserApi();

    const stats = useAsync(async () => {
      const { data } = await api.households.statistics();

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
      totalCategories: $globals.icons.categories,
      totalTags: $globals.icons.tags,
      totalTools: $globals.icons.potSteam,
    };

    function getStatsIcon(key: string) {
      return iconText[key] ?? $globals.icons.primary;
    }

    const statsTo = computed<{ [key: string]: string }>(() => {
      return {
        totalRecipes: `/g/${groupSlug.value}/`,
        totalUsers: "/household/members",
        totalCategories: `/g/${groupSlug.value}/recipes/categories`,
        totalTags: `/g/${groupSlug.value}/recipes/tags`,
        totalTools: `/g/${groupSlug.value}/recipes/tools`,
      }
    });

    function getStatsTo(key: string) {
      return statsTo.value[key] ?? "unknown";
    }

    return {
      groupSlug,
      getStatsTitle,
      getStatsIcon,
      getStatsTo,
      inviteDialog,
      stats,
      user,
    };
  },
  head() {
    return {
      title: this.$t("settings.profile") as string,
    };
  },
});
</script>
