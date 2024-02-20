import { ref, Ref, useContext } from "@nuxtjs/composition-api";
import { useAsyncValidator } from "~/composables/use-validators";
import { VForm } from "~/types/vuetify";
import { usePublicApi } from "~/composables/api/api-client";

const domAccountForm = ref<VForm | null>(null);
const username = ref("");
const fullName = ref("");
const email = ref("");
const password1 = ref("");
const password2 = ref("");
const advancedOptions = ref(false);

export const useUserRegistrationForm = () => {
  const { i18n } = useContext();
  function safeValidate(form: Ref<VForm | null>) {
    if (form.value && form.value.validate) {
      return form.value.validate();
    }
    return false;
  }
  // ================================================================
  // Provide Group Details
  const publicApi = usePublicApi();
  // ================================================================
  // Provide Account Details

  const usernameErrorMessages = ref<string[]>([]);
  const { validate: validateUsername, valid: validUsername } = useAsyncValidator(
    username,
    (v: string) => publicApi.validators.username(v),
    i18n.tc("validation.username-is-taken"),
    usernameErrorMessages
  );
  const emailErrorMessages = ref<string[]>([]);
  const { validate: validateEmail, valid: validEmail } = useAsyncValidator(
    email,
    (v: string) => publicApi.validators.email(v),
    i18n.tc("validation.email-is-taken"),
    emailErrorMessages
  );
  const accountDetails = {
    username,
    fullName,
    email,
    advancedOptions,
    validate: async () => {
      if (!(validUsername.value && validEmail.value)) {
        await Promise.all([validateUsername(), validateEmail()]);
      }

      return (safeValidate(domAccountForm as Ref<VForm>) && validUsername.value && validEmail.value);
    },
    reset: () => {
      accountDetails.username.value = "";
      accountDetails.fullName.value = "";
      accountDetails.email.value = "";
      accountDetails.advancedOptions.value = false;
    },
  };
  // ================================================================
  // Provide Credentials
  const passwordMatch = () => password1.value === password2.value || i18n.tc("user.password-must-match");
  const credentials = {
    password1,
    password2,
    passwordMatch,
    reset: () => {
      credentials.password1.value = "";
      credentials.password2.value = "";
    }
  };

  return {
    accountDetails,
    credentials,
    emailErrorMessages,
    usernameErrorMessages,
    // Fields
    advancedOptions,
    // Validators
    validateUsername,
    validateEmail,
    // Dom Refs
    domAccountForm,
  };
};
