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
        <v-subheader>{{$t('meal-plan.dinner-tonight')}}</v-subheader>
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

      <v-virtual-scroll v-if="currentGroup.users" :items="currentGroup.users" height="257" item-height="64">
        <template v-slot:default="{ item }">
          <v-list-item :key="item.id" @click.prevent>
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
          </v-list-item>
          <v-divider></v-divider>
        </template>
      </v-virtual-scroll>

      <div class="mt-3">
        <h3 class="display-2 font-weight-light text--primary">
          <v-icon x-large>
            mdi-food-variant
          </v-icon>
          <small> {{$t('meal-plan.mealplan-settings')}} </small>
        </h3>
      </div>
      <v-divider></v-divider>

      <v-subheader>{{$t('meal-plan.mealplan-categories')}}</v-subheader>
      <v-card-text class="mt-0 pt-0">
        {{ $t("meal-plan.only-recipes-with-these-categories-will-be-used-in-meal-plans") }}
      </v-card-text>
      <CategoryTagSelector
        :solo="true"
        :dense="false"
        v-model="groupSettings.categories"
        :return-object="true"
        :show-add="true"
      />

      <v-divider></v-divider>
      <v-subheader>{{$t('settings.webhooks.webhooks-caps')}}</v-subheader>
      <v-card-text class="mt-0 pt-0">
        {{
          $t(
            "settings.webhooks.the-urls-listed-below-will-recieve-webhooks-containing-the-recipe-data-for-the-meal-plan-on-its-scheduled-day-currently-webhooks-will-execute-at"
          )
        }}
        <strong>{{ groupSettings.webhookTime }}</strong>
      </v-card-text>
      <v-row dense class="flex align-center">
        <v-switch class="ml-5 mr-auto" v-model="groupSettings.webhookEnable" :label="$t('general.enabled')"></v-switch>
        <TimePickerDialog @save-time="saveTime" class="" />
      </v-row>

      <v-card-text>
        <v-text-field
          prepend-icon="mdi-delete"
          v-for="(url, index) in groupSettings.webhookUrls"
          @click:prepend="removeWebhook(index)"
          :key="index"
          v-model="groupSettings.webhookUrls[index]"
          :label="$t('settings.webhooks.webhook-url')"
        ></v-text-field>
        <v-card-actions class="pa-0">
          <v-spacer></v-spacer>
          <v-btn small color="success" @click="addWebhook">
            <v-icon left> mdi-webhook </v-icon>
            {{$t('general.new')}}
          </v-btn>
        </v-card-actions>
      </v-card-text>

      <v-divider></v-divider>
      <v-card-actions class="pb-0">
        <v-btn class="ma-2" color="info" @click="testWebhooks">
          <v-icon left> mdi-webhook </v-icon>
          {{ $t("settings.webhooks.test-webhooks") }}
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn color="success" @click="saveGroupSettings">
          <v-icon left> mdi-content-save </v-icon>
          {{ $t("general.update") }}
        </v-btn>
      </v-card-actions>
    </template>
  </StatCard>
</template>

<script>
import TimePickerDialog from "@/components/FormHelpers/TimePickerDialog";
import CategoryTagSelector from "@/components/FormHelpers/CategoryTagSelector";
import StatCard from "@/components/UI/StatCard";
import MobileRecipeCard from "@/components/Recipe/MobileRecipeCard";
import { validators } from "@/mixins/validators";
import { initials } from "@/mixins/initials";
import { api } from "@/api";
export default {
  components: {
    StatCard,
    MobileRecipeCard,
    CategoryTagSelector,
    TimePickerDialog,
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
      groupSettings: {},
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

  async mounted() {
    this.getTodaysMeal();
    await this.$store.dispatch("requestCurrentGroup");
    this.getSiteSettings();
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
    getSiteSettings() {
      this.groupSettings = this.$store.getters.getCurrentGroup;
    },
    saveTime(value) {
      this.groupSettings.webhookTime = value;
    },
    addWebhook() {
      this.groupSettings.webhookUrls.push(" ");
    },
    removeWebhook(index) {
      this.groupSettings.webhookUrls.splice(index, 1);
    },
    async saveGroupSettings() {
      if (await api.groups.update(this.groupSettings)) {
        await this.$store.dispatch("requestCurrentGroup");
        this.getSiteSettings();
      }
    },
    testWebhooks() {
      api.settings.testWebhooks();
    },
  },
};
</script>

<style></style>
