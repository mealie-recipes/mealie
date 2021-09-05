<template>
  <v-container fill-height fluid class="d-flex justify-center align-start narrow-container">
    <v-card color="background d-flex flex-column align-center" flat width="700px">
      <v-card-title class="headline"> User Registration </v-card-title>
      <v-card-text>
        <v-form ref="domRegisterForm" @submit.prevent="register()">
          <ToggleState>
            <template #activator="{ toggle }">
              <div class="d-flex justify-center my-2">
                <v-btn-toggle tile mandatory group color="primary">
                  <v-btn small @click="toggle(false)"> Create a Group </v-btn>
                  <v-btn small @click="toggle(true)"> Join a Group </v-btn>
                </v-btn-toggle>
              </div>
            </template>
            <template #default="{ state }">
              <v-text-field
                v-if="!state"
                v-model="form.group"
                filled
                rounded
                autofocus
                validate-on-blur
                class="rounded-lg"
                :prepend-icon="$globals.icons.group"
                :rules="[tokenOrGroup]"
                label="New Group Name"
              />
              <v-text-field
                v-else
                v-model="form.groupToken"
                filled
                rounded
                validate-on-blur
                :rules="[tokenOrGroup]"
                class="rounded-lg"
                :prepend-icon="$globals.icons.group"
                label="Group Token"
              />
            </template>
          </ToggleState>
          <v-text-field
            v-model="form.email"
            filled
            rounded
            class="rounded-lg"
            validate-on-blur
            :prepend-icon="$globals.icons.email"
            label="Email"
            :rules="[validators.required, validators.email]"
          />
          <v-text-field
            v-model="form.username"
            filled
            rounded
            class="rounded-lg"
            :prepend-icon="$globals.icons.user"
            label="Username"
            :rules="[validators.required]"
          />
          <v-text-field
            v-model="form.password"
            filled
            rounded
            class="rounded-lg"
            :prepend-icon="$globals.icons.lock"
            name="password"
            label="Password"
            type="password"
            :rules="[validators.required]"
          />
          <v-text-field
            v-model="form.passwordConfirm"
            filled
            rounded
            validate-on-blur
            class="rounded-lg"
            :prepend-icon="$globals.icons.lock"
            name="password"
            label="Confirm Password"
            type="password"
            :rules="[validators.required, passwordMatch]"
          />
          <div class="mt-n4 px-8">
            <v-checkbox v-model="form.private" label="Keep My Recipes Private"></v-checkbox>
            <p class="text-caption mt-n4">
              Sets your group and all recipes defaults to private. You can always change this later.
            </p>
            <v-checkbox v-model="form.advanced" label="Enable Advanced Content"></v-checkbox>
            <p class="text-caption mt-n4">
              Enables advanced features like Recipe Scaling, API keys, Webhooks, and Data Management. Don't worry, you
              can always change this later
            </p>
          </div>
          <v-btn :loading="loggingIn" color="primary" type="submit" large rounded class="rounded-xl" block>
            Register
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, ref } from "@nuxtjs/composition-api";
import { validators } from "@/composables/use-validators";
import { useApiSingleton } from "~/composables/use-api";

export default defineComponent({
  layout: "basic",
  setup() {
    const api = useApiSingleton();
    const state = reactive({
      loggingIn: false,
      success: false,
    });
    const allowSignup = computed(() => process.env.AllOW_SIGNUP);

    // @ts-ignore
    const domRegisterForm = ref<VForm>(null);

    const form = reactive({
      group: "",
      groupToken: "",
      email: "",
      username: "",
      password: "",
      passwordConfirm: "",
      advanced: false,
      private: false,
    });

    const passwordMatch = () => form.password === form.passwordConfirm || "Passwords do not match";
    const tokenOrGroup = () => form.group !== "" || form.groupToken !== "" || "Group name or token must be given";

    async function register() {
      if (!domRegisterForm.value?.validate()) {
        return;
      }

      const { data, response } = await api.register.register(form);

      if (response?.status === 201) {
        state.success = true;
      }

      console.log(data, response);
    }

    return {
      domRegisterForm,
      validators,
      allowSignup,
      form,
      ...toRefs(state),
      passwordMatch,
      tokenOrGroup,
      register,
    };
  },
});
</script>