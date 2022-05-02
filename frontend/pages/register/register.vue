<template>
  <v-container
    fill-height
    fluid
    class="d-flex justify-center align-center"
    :class="{
      'bg-off-white': !$vuetify.theme.dark && !isDark.value,
    }"
  >
    <LanguageDialog v-model="langDialog" />

    <v-card class="d-flex flex-column" width="1200px" min-height="700px">
      <div>
        <v-toolbar width="100%" color="primary" class="d-flex justify-center" style="margin-bottom: 4rem" dark>
          <v-toolbar-title class="headline text-h4"> Mealie </v-toolbar-title>
        </v-toolbar>

        <div class="icon-container">
          <v-divider class="icon-divider"></v-divider>
          <v-avatar class="pa-2 icon-avatar" color="primary" size="75">
            <svg class="icon-white" style="width: 75; height: 17500px" viewBox="0 0 24 24">
              <path
                d="M8.1,13.34L3.91,9.16C2.35,7.59 2.35,5.06 3.91,3.5L10.93,10.5L8.1,13.34M13.41,13L20.29,19.88L18.88,21.29L12,14.41L5.12,21.29L3.71,19.88L13.36,10.22L13.16,10C12.38,9.23 12.38,7.97 13.16,7.19L17.5,2.82L18.43,3.74L15.19,7L16.15,7.94L19.39,4.69L20.31,5.61L17.06,8.85L18,9.81L21.26,6.56L22.18,7.5L17.81,11.84C17.03,12.62 15.77,12.62 15,11.84L14.78,11.64L13.41,13Z"
              />
            </svg>
          </v-avatar>
        </div>
      </div>

      <!-- Form Container -->
      <div class="d-flex justify-center grow items-center my-4">
        <template v-if="state.ctx.state === States.Initial">
          <div width="600px">
            <v-card-title class="headline justify-center my-4 mb-5 pb-0"> User Registration </v-card-title>

            <div class="d-flex flex-wrap justify-center flex-md-nowrap pa-4" style="gap: 1em">
              <v-card color="primary" dark hover width="300px" outlined @click="initial.joinGroup">
                <v-card-title class="justify-center">
                  <v-icon large left> {{ $globals.icons.group }}</v-icon>

                  Join Existing Group
                </v-card-title>
              </v-card>
              <v-card color="primary" dark hover width="300px" outlined @click="initial.createGroup">
                <v-card-title class="justify-center">
                  <v-icon large left> {{ $globals.icons.user }}</v-icon>

                  Create A New Group
                </v-card-title>
              </v-card>
            </div>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.ProvideToken">
          <div>
            <v-card-title>
              <v-icon large class="mr-3"> {{ $globals.icons.group }}</v-icon>
              <span class="headline">Join a Group</span>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              Please provide the registration token associated with the group that you'd like to join. You'll need to
              obtain this from an existing group member.
              <v-form ref="domTokenForm" class="mt-4" @submit.prevent>
                <v-text-field v-model="token" v-bind="inputAttrs" label="Group Token" :rules="[validators.required]" />
              </v-form>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions class="mt-auto justify-space-between">
              <BaseButton cancel @click="state.back">
                <template #icon> {{ $globals.icons.back }}</template>
                Back
              </BaseButton>
              <BaseButton icon-right @click="provideToken.next">
                <template #icon> {{ $globals.icons.forward }}</template>
                Next
              </BaseButton>
            </v-card-actions>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.ProvideGroupDetails">
          <div>
            <v-card-title>
              <v-icon large class="mr-3"> {{ $globals.icons.group }}</v-icon>
              <span class="headline">Group Details</span>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <v-form ref="domGroupForm" @submit.prevent>
                <v-text-field
                  v-model="groupDetails.groupName.value"
                  v-bind="inputAttrs"
                  label="Group Name"
                  :rules="[validators.required]"
                />
                <div class="mt-n4 px-2">
                  <v-checkbox v-model="groupDetails.groupPrivate.value" label="Keep My Recipes Private"></v-checkbox>
                  <p class="text-caption mt-n4">
                    Sets your group and all recipes defaults to private. You can always change this later.
                  </p>

                  <v-checkbox v-model="groupDetails.groupSeed.value" label="Use Seed Data"></v-checkbox>
                  <p class="text-caption mt-n4">
                    Mealie ships with a collection of Foods, Units, and Labels that can be used to populate your group
                    with helpful data for organizing your recipes.
                  </p>
                </div>
              </v-form>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions class="justify-space-between">
              <BaseButton cancel @click="state.back">
                <template #icon> {{ $globals.icons.back }}</template>
                Back
              </BaseButton>
              <BaseButton icon-right @click="groupDetails.next">
                <template #icon> {{ $globals.icons.forward }}</template>
                Next
              </BaseButton>
            </v-card-actions>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.ProvideAccountDetails">
          <div>
            <v-card-title>
              <v-icon large class="mr-3"> {{ $globals.icons.user }}</v-icon>
              <span class="headline"> Account Details</span>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <v-form ref="domAccountForm" @submit.prevent>
                <v-text-field
                  v-model="accountDetails.username.value"
                  autofocus
                  v-bind="inputAttrs"
                  label="Username"
                  :prepend-icon="$globals.icons.user"
                  :rules="[validators.required]"
                />
                <v-text-field
                  v-model="accountDetails.email.value"
                  v-bind="inputAttrs"
                  :prepend-icon="$globals.icons.email"
                  label="Email"
                  :rules="[validators.required, validators.email]"
                />
                <v-text-field
                  v-model="credentials.password1.value"
                  v-bind="inputAttrs"
                  :prepend-icon="$globals.icons.lock"
                  type="password"
                  label="Password"
                  :rules="[validators.required, ...pwValidators.passwordValidators]"
                />
                <v-text-field
                  v-model="credentials.password2.value"
                  v-bind="inputAttrs"
                  :prepend-icon="$globals.icons.lock"
                  type="password"
                  label="Confirm Password"
                  :rules="[validators.required, credentials.passwordMatch]"
                />
                <v-expand-transition>
                  <v-card v-show="credentials.password1.value" class="pt-2" flat outlined>
                    <template v-if="!pwValidators.isValid.value">
                      <strong class="pl-2 pb-1"> Password Requirements </strong>
                      <ul class="px-2">
                        <li
                          v-for="(vd, i) in [
                            pwValidators.validateNumber,
                            pwValidators.validateSpecialCharacter,
                            pwValidators.validatorLength,
                            pwValidators.validatorLowerCase,
                            pwValidators.validatorUpperCase,
                          ]"
                          :key="i"
                          class="d-flex align-center"
                        >
                          <v-icon class="mt-0" :color="vd.met.value ? 'success' : 'error'">
                            {{ vd.met.value ? $globals.icons.check : $globals.icons.close }}
                          </v-icon>
                          {{ vd.label }}
                        </li>
                      </ul>
                    </template>
                    <template v-else>
                      <ul class="px-2">
                        <li class="d-flex align-center">
                          <v-icon class="mt-0" color="success"> {{ $globals.icons.check }}</v-icon>
                          Password meets all requirements
                        </li>
                      </ul>
                    </template>
                  </v-card>
                </v-expand-transition>
                <div class="px-2">
                  <v-checkbox
                    v-model="accountDetails.advancedOptions.value"
                    label="Enable Advanced Content"
                  ></v-checkbox>
                  <p class="text-caption mt-n4">
                    Enables advanced features like Recipe Scaling, API keys, Webhooks, and Data Management. Don't worry,
                    you can always change this later
                  </p>
                </div>
              </v-form>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions class="justify-space-between">
              <BaseButton cancel @click="state.back">
                <template #icon> {{ $globals.icons.back }}</template>
                Back
              </BaseButton>
              <BaseButton icon-right @click="accountDetails.next">
                <template #icon> {{ $globals.icons.forward }}</template>
                Next
              </BaseButton>
            </v-card-actions>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.Confirmation">
          <div style="width: 830px">
            <v-card-title class="mb-0 pb-0">
              <v-icon large class="mr-3"> {{ $globals.icons.user }}</v-icon>
              <span class="headline">Confirmation</span>
            </v-card-title>
            <v-list>
              <v-list-item v-if="state.ctx.type === RegistrationType.JoinGroup">
                <v-list-item-content>
                  <v-list-item-title> Joining Group </v-list-item-title>
                  <v-list-item-subtitle> {{ groupDetails.groupName.value }} </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <template v-else-if="state.ctx.type === RegistrationType.CreateGroup">
                <v-divider></v-divider>

                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title> Creating Group </v-list-item-title>
                    <v-list-item-subtitle> {{ groupDetails.groupName.value }} </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-divider></v-divider>

                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title> Seed Group Data </v-list-item-title>
                    <v-list-item-subtitle> {{ groupDetails.groupSeed.value ? "Yes" : "No" }} </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-divider></v-divider>

                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title> Private Group </v-list-item-title>
                    <v-list-item-subtitle> {{ groupDetails.groupPrivate.value ? "Yes" : "No" }} </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </template>
              <v-divider></v-divider>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title> Username </v-list-item-title>
                  <v-list-item-subtitle> {{ accountDetails.username.value }} </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-divider></v-divider>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title> Email </v-list-item-title>
                  <v-list-item-subtitle> {{ accountDetails.email.value }} </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-divider></v-divider>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title> Advanced User Options </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ accountDetails.advancedOptions.value ? "Yes" : "No" }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>

            <v-divider></v-divider>
            <v-card-actions class="justify-space-between">
              <BaseButton cancel @click="state.back">
                <template #icon> {{ $globals.icons.back }}</template>
                Back
              </BaseButton>
              <BaseButton @click="submitRegistration">
                <template #icon> {{ $globals.icons.check }}</template>
                Submit
              </BaseButton>
            </v-card-actions>
          </div>
        </template>
      </div>
      <v-card-actions class="justify-center py-8">
        <BaseButton large color="primary" @click="langDialog = true">
          <template #icon> {{ $globals.icons.translate }}</template>
          Select Language
        </BaseButton>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, useRouter, Ref } from "@nuxtjs/composition-api";
import { useDark } from "@vueuse/core";
import { States, RegistrationType, useRegistration } from "./states";
import { useRouteQuery } from "~/composables/use-router";
import { validators, usePasswordValidator } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { CreateUserRegistration } from "~/types/api-types/user";
import { VForm } from "~/types/vuetify";

const inputAttrs = {
  filled: true,
  rounded: true,
  validateOnBlur: true,
  class: "rounded-lg",
};

export default defineComponent({
  layout: "basic",
  setup() {
    const isDark = useDark();

    function safeValidate(form: Ref<VForm | null>) {
      if (form.value && form.value.validate) {
        return form.value.validate();
      }
      return false;
    }

    // ================================================================
    // Registration Context
    //
    // State is used to manage the registration process states and provide
    // a state machine esq interface to interact with the registration workflow.
    const state = useRegistration();

    // ================================================================
    // Handle Token URL / Initialization
    //

    const token = useRouteQuery("token");

    // TODO: We need to have some way to check to see if the site is in a state
    // Where it needs to be initialized with a user, in that case we'll handle that
    // somewhere...
    function initialUser() {
      return false;
    }

    onMounted(() => {
      if (token.value) {
        state.setState(States.ProvideAccountDetails);
        state.setType(RegistrationType.JoinGroup);
      }

      if (initialUser()) {
        state.setState(States.ProvideGroupDetails);
        state.setType(RegistrationType.InitialGroup);
      }
    });

    // ================================================================
    // Initial

    const initial = {
      createGroup: () => {
        state.setState(States.ProvideGroupDetails);
        state.setType(RegistrationType.CreateGroup);
        token.value = null;
      },
      joinGroup: () => {
        state.setState(States.ProvideToken);
        state.setType(RegistrationType.JoinGroup);
      },
    };

    // ================================================================
    // Provide Token

    const domTokenForm = ref<VForm | null>(null);

    function validateToken() {
      return true;
    }

    const provideToken = {
      next: () => {
        if (!safeValidate(domTokenForm as Ref<VForm>)) {
          return;
        }

        if (validateToken()) {
          state.setState(States.ProvideAccountDetails);
        }
      },
    };

    // ================================================================
    // Provide Group Details

    const domGroupForm = ref<VForm | null>(null);

    const groupName = ref("");
    const groupSeed = ref(false);
    const groupPrivate = ref(false);

    const groupDetails = {
      groupName,
      groupSeed,
      groupPrivate,
      next: () => {
        if (!safeValidate(domGroupForm as Ref<VForm>)) {
          return;
        }

        state.setState(States.ProvideAccountDetails);
      },
    };

    // ================================================================
    // Provide Account Details

    const domAccountForm = ref<VForm | null>(null);

    const username = ref("");
    const email = ref("");
    const advancedOptions = ref(false);

    const accountDetails = {
      username,
      email,
      advancedOptions,
      next: () => {
        if (!safeValidate(domAccountForm as Ref<VForm>)) {
          return;
        }

        state.setState(States.Confirmation);
      },
    };

    // ================================================================
    // Provide Credentials

    const password1 = ref("");
    const password2 = ref("");

    const pwValidators = usePasswordValidator(password1);

    const passwordMatch = () => password1.value === password2.value || "Passwords do not match";

    const credentials = {
      password1,
      password2,
      passwordMatch,
    };

    // ================================================================
    // Confirmation

    const api = useUserApi();
    const router = useRouter();

    async function submitRegistration() {
      const payload: CreateUserRegistration = {
        email: email.value,
        username: username.value,
        password: password1.value,
        passwordConfirm: password2.value,
        // groupSeed: groupSeed.value, // Future!
      };

      if (state.ctx.type === RegistrationType.CreateGroup) {
        payload.group = groupName.value;
        payload.advanced = advancedOptions.value;
        payload.private = groupPrivate.value;
      } else {
        payload.groupToken = token.value;
      }

      const { response } = await api.register.register(payload);

      if (response?.status === 201) {
        alert.success("Registration Success");
        router.push("/login");
      }
    }

    const langDialog = ref(false);

    return {
      pwValidators,
      langDialog,
      isDark,
      States,
      RegistrationType,
      state,
      inputAttrs,
      validators,
      initial,
      provideToken,
      accountDetails,
      credentials,
      groupDetails,
      token,
      submitRegistration,

      // Dom Refs
      domAccountForm,
      domGroupForm,
      domTokenForm,
    };
  },
});
</script>

<style lang="css">
.icon-primary {
  fill: var(--v-primary-base);
}

.icon-white {
  fill: white;
}

.icon-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
  margin-top: 2.5rem;
}

.icon-divider {
  width: 100%;
  margin-bottom: -2.5rem;
}

.icon-avatar {
  border-color: rgba(0, 0, 0, 0.12);
  border: 2px;
}

.bg-off-white {
  background: #f5f8fa;
}
</style>
