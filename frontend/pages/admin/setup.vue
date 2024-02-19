<template>
  <v-container
    fill-height
    fluid
    class="d-flex justify-center align-center"
    width="1200px"
    min-height="700px"
    :class="{
      'bg-off-white': !$vuetify.theme.dark,
    }"
  >
    <Wizard
      v-model="currentPage"
      :max-page-number="totalPages"
      :title="$i18n.tc('admin.first-time-setup')"
      :prev-button-show="activeConfig.showPrevButton"
      :next-button-show="activeConfig.showNextButton"
      :next-button-text="activeConfig.nextButtonText"
      :next-button-icon="activeConfig.nextButtonIcon"
      :next-button-color="activeConfig.nextButtonColor"
      :next-button-is-submit="activeConfig.isSubmit"
      :is-submitting="isSubmitting"
      @submit="handleSubmit"
    >
    <v-container v-if="currentPage === Pages.LANDING" class="mb-12">
      <v-card-title class="text-h4 justify-center">
        {{ $i18n.tc('admin.welcome-to-mealie-get-started') }}
      </v-card-title>
      <v-btn
        rounded
        outlined
        text
        color="grey lighten-1"
        class="text-subtitle-2 d-flex mx-auto"
      >
        {{ $i18n.tc('admin.already-set-up-bring-to-homepage') }}
      </v-btn>
    </v-container>
    <v-container v-if="currentPage === Pages.USER_INFO">
      <UserRegistrationForm />
    </v-container>
    <v-container v-if="currentPage === Pages.PAGE_2">
      <v-card-text>Page 2</v-card-text>
    </v-container>
    <v-container v-if="currentPage === Pages.CONFIRM">
      <v-card-text>Confirm Page</v-card-text>
    </v-container>
    <v-container v-if="currentPage === Pages.END">
      <v-card-text>End Page</v-card-text>
    </v-container>
    </Wizard>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext, useRouter } from "@nuxtjs/composition-api";
import { useUserRegistrationForm } from "~/composables/use-users/user-registration-form";
import UserRegistrationForm from "~/components/Domain/User/UserRegistrationForm.vue";

export default defineComponent({
  components: { UserRegistrationForm },
  layout: "blank",
  setup() {
    const { $auth, $globals, i18n } = useContext();
    const { accountDetails } = useUserRegistrationForm();

    const groupSlug = computed(() => $auth.user?.groupSlug);
    const router = useRouter();
    const isSubmitting = ref(false);

    if (!$auth.loggedIn) {
      router.push("/login");
    }

    type Config = {
      nextButtonText: string | undefined;
      nextButtonIcon: string | undefined;
      nextButtonColor: string | undefined;
      showPrevButton: boolean;
      showNextButton: boolean;
      isSubmit: boolean;
    }

    const totalPages = 4;
    enum Pages {
      LANDING = 0,
      USER_INFO = 1,
      PAGE_2 = 2,
      CONFIRM = 3,
      END = 4,
    }

    const currentPage = ref(0);
    const activeConfig = computed<Config>(() => {
      const config: Config = {
        nextButtonText: undefined,
        nextButtonIcon: undefined,
        nextButtonColor: undefined,
        showPrevButton: true,
        showNextButton: true,
        isSubmit: false,
      }

      switch (currentPage.value) {
        case Pages.LANDING:
          config.showPrevButton = false;
          config.nextButtonText = i18n.tc("general.start");
          config.nextButtonIcon = $globals.icons.forward;
          break;
        case Pages.USER_INFO:
          config.showPrevButton = false;
          config.nextButtonText = i18n.tc("general.next");
          config.nextButtonIcon = $globals.icons.forward;
          config.isSubmit = true;
        case Pages.CONFIRM:
          config.isSubmit = true;
          break;
        case Pages.END:
          config.nextButtonText = i18n.tc("general.home");
          config.nextButtonIcon = $globals.icons.home;
          config.nextButtonColor = "primary";
          config.showPrevButton = false;
          config.isSubmit = true;
          break;
      }

      return config;
    })

    async function handleSubmit(page: number) {
      if (isSubmitting.value) {
        return;
      }

      isSubmitting.value = true;
      switch (page) {
        case Pages.USER_INFO:
          if (await accountDetails.validate()) {
            currentPage.value += 1;
          }
          break;
        case Pages.CONFIRM:
          // TODO: handle submit
          currentPage.value += 1;
          break;
        case Pages.END:
          router.push(groupSlug.value ? `/g/${groupSlug.value || ""}` : "/login");
          break;
      }
      isSubmitting.value = false;
    }

    return {
      Pages,
      currentPage,
      totalPages,
      activeConfig,
      isSubmitting,
      handleSubmit,
    }
  },

  header() {
    return {
      title: this.$i18n.tc("admin.first-time-setup"),
    };
  },
})
</script>
