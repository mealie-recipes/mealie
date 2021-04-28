<template>
  <v-card>
    <v-card-title class="headline">
      {{ $t("meal-plan.meal-planner") }}
    </v-card-title>
    <v-divider></v-divider>
    <v-card-text>
      <h2 class="mt-1">{{ $t("recipe.categories") }}</h2>

      <CategoryTagSelector
        class="mt-4"
        :solo="true"
        :dense="false"
        v-model="groupSettings.categories"
        :return-object="true"
        :show-add="true"
        :hint="
          $t(
            'meal-plan.only-recipes-with-these-categories-will-be-used-in-meal-plans'
          )
        "
      />
    </v-card-text>
    <v-divider> </v-divider>
    <v-card-text>
      <h2 class="mt-1 mb-4">
        {{ $t("settings.webhooks.meal-planner-webhooks") }}
      </h2>
      <p>
        {{
          $t(
            "settings.webhooks.the-urls-listed-below-will-recieve-webhooks-containing-the-recipe-data-for-the-meal-plan-on-its-scheduled-day-currently-webhooks-will-execute-at"
          )
        }}
        <strong>{{ groupSettings.webhookTime }}</strong>
      </p>

      <v-row dense class="flex align-center">
        <v-switch
          class="mx-2"
          v-model="groupSettings.webhookEnable"
          :label="$t('general.enabled')"
        ></v-switch>
        <TimePickerDialog @save-time="saveTime" class="ma-2" />
        <v-btn class="ma-2" color="info" @click="testWebhooks">
          <v-icon left> mdi-webhook </v-icon>
          {{ $t("settings.webhooks.test-webhooks") }}
        </v-btn>
      </v-row>

      <v-row
        v-for="(url, index) in groupSettings.webhookUrls"
        :key="index"
        align=" center"
        dense
      >
        <v-col cols="1">
          <v-btn icon color="error" @click="removeWebhook(index)">
            <v-icon>mdi-minus</v-icon>
          </v-btn>
        </v-col>
        <v-col>
          <v-text-field
            v-model="groupSettings.webhookUrls[index]"
            :label="$t('settings.webhooks.webhook-url')"
          ></v-text-field>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-btn icon color="success" @click="addWebhook">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn color="success" @click="saveGroupSettings" class="mr-2 mb-1">
        <v-icon left> mdi-content-save </v-icon>
        {{ $t("general.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { api } from "@/api";
import TimePickerDialog from "@/components/FormHelpers/TimePickerDialog";
import CategoryTagSelector from "@/components/FormHelpers/CategoryTagSelector";
export default {
  components: {
    TimePickerDialog,
    CategoryTagSelector,
  },
  data() {
    return {
      groupSettings: {
        name: "home",
        id: 1,
        mealplans: [],
        categories: [],
        webhookUrls: [],
        webhookTime: "00:00",
        webhookEnable: false,
      },
    };
  },
  async mounted() {
    await this.$store.dispatch("requestCurrentGroup");
    this.getSiteSettings();
  },
  computed: {
    categories() {
      return this.$store.getters.getAllCategories;
    },
    isFlat() {
      return this.groupSettings.categories >= 1 ? true : false;
    },
  },
  methods: {
    saveTime(value) {
      this.groupSettings.webhookTime = value;
    },
    getSiteSettings() {
      let settings = this.$store.getters.getCurrentGroup;

      this.groupSettings.name = settings.name;
      this.groupSettings.id = settings.id;
      this.groupSettings.categories = settings.categories;
      this.groupSettings.webhookUrls = settings.webhookUrls;
      this.groupSettings.webhookTime = settings.webhookTime;
      this.groupSettings.webhookEnable = settings.webhookEnable;
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

<style>
</style>