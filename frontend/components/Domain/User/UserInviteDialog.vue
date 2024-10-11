<template>
  <BaseDialog
    v-model="inviteDialog"
    :title="$tc('profile.get-invite-link')"
    :icon="$globals.icons.accountPlusOutline" color="primary">
    <v-container>
      <v-form class="mt-5">
        <v-select
v-if="groups && groups.length" v-model="selectedGroup" :items="groups" item-text="name"
          item-value="id" :return-object="false" filled :label="$tc('group.user-group')"
          :rules="[validators.required]" />
        <v-select
v-if="households && households.length" v-model="selectedHousehold" :items="filteredHouseholds"
          item-text="name" item-value="id" :return-object="false" filled :label="$tc('household.user-household')"
          :rules="[validators.required]" />
        <v-row>
          <v-col cols="9">
            <v-text-field :label="$tc('profile.invite-link')" type="text" readonly filled :value="generatedSignupLink" />
          </v-col>
          <v-col cols="3" class="pl-1 mt-3">
            <AppButtonCopy
:icon="false" color="info" :copy-text="generatedSignupLink"
              :disabled="generatedSignupLink" />
          </v-col>
        </v-row>
        <v-text-field
v-model="sendTo" :label="$t('user.email')" :rules="[validators.email]" outlined
          @keydown.enter="sendInvite" />
      </v-form>
    </v-container>
    <template #custom-card-action>
      <BaseButton :disabled="!validEmail" :loading="loading" :icon="$globals.icons.email" @click="sendInvite">
        {{ $t("group.invite") }}
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<script lang="ts">
import { computed, defineComponent, useContext, ref, toRefs, reactive } from "@nuxtjs/composition-api";
import { useUserApi } from "@/composables/api";
import BaseDialog from "~/components/global/BaseDialog.vue";
import AppButtonCopy from "~/components/global/AppButtonCopy.vue";
import BaseButton from "~/components/global/BaseButton.vue";
import { validators } from "~/composables/use-validators";
import { alert } from "~/composables/use-toast";
import { GroupInDB } from "~/lib/api/types/user";
import { HouseholdInDB } from "~/lib/api/types/household";

export default defineComponent({
  name: "UserInviteDialog",
  components: {
    BaseDialog,
    AppButtonCopy,
    BaseButton,
  },
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    showLink: {
      type: Boolean,
      default: true,
    },
    groups: {
      type: Array as () => (GroupInDB[] | null),
      default: null,
    },
    households: {
      type: Array as () => (HouseholdInDB[] | null),
      default: null,
    },
  },
  setup(props, context) {
    const { i18n } = useContext();

    const token = ref("");
    const selectedGroup = ref<string | null>(null);
    const selectedHousehold = ref<string | null>(null);
    const api = useUserApi();

    const inviteDialog = computed<boolean>({
      get() {
        return props.value;
      },
      set(val) {
        context.emit("input", val);
      },
    });

    async function getSignupLink(group: string | null = null, household: string | null = null) {
      const payload = (group && household) ? { uses: 1, group_id: group, household_id: household } : { uses: 1 };
      const { data } = await api.households.createInvitation(payload);
      if (data) {
        token.value = data.token;
      }
    }

    const filteredHouseholds = computed(() => {
      if (!selectedGroup.value) return [];
      return props.households?.filter(household => household.groupId === selectedGroup.value);
    });

    function constructLink(token: string) {
      return token ? `${window.location.origin}/register?token=${token}` : "";
    }

    const generatedSignupLink = computed(() => {
      return constructLink(token.value);
    });

    // =================================================
    // Email Invitation
    const state = reactive({
      loading: false,
      sendTo: "",
    });

    async function sendInvite() {
      state.loading = true;
      if (!token.value) {
        getSignupLink(selectedGroup.value, selectedHousehold.value);
      }
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
      inviteDialog.value = false;
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
      sendInvite,
      validators,
      validEmail,
      inviteDialog,
      getSignupLink,
      generatedSignupLink,
      selectedGroup,
      selectedHousehold,
      filteredHouseholds,
      ...toRefs(state),
    };
  },
  watch: {
    value: {
      immediate: false,
      handler(val) {
        if (val && !this.groups) {
          this.getSignupLink();
        }
      },
    },
    selectedHousehold(newVal) {
      if (newVal && this.selectedGroup) {
        this.getSignupLink();
      }
    },
  },

});
</script>
