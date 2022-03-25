import { ref, Ref } from "@nuxtjs/composition-api";
import { RequestResponse } from "~/types/api";
import { ValidationResponse } from "~/types/api-types/response";

const EMAIL_REGEX =
  /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@(([[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

const URL_REGEX = /[-a-zA-Z0-9@:%._+~#=]{1,256}.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)/;

export const validators = {
  required: (v: string) => !!v || "This Field is Required",
  email: (v: string) => !v || EMAIL_REGEX.test(v) || "Email Must Be Valid",
  whitespace: (v: string) => !v || v.split(" ").length <= 1 || "No Whitespace Allowed",
  url: (v: string) => !v || URL_REGEX.test(v) || "Must Be A Valid URL",
  minLength: (min: number) => (v: string) => !v || v.length >= min || `Must Be At Least ${min} Characters`,
  maxLength: (max: number) => (v: string) => !v || v.length <= max || `Must Be At Most ${max} Characters`,
};

/**
 * useAsyncValidator us a factory function that returns an async function that
 * when called will validate the input against the backend database and set the
 * error messages when applicable to the ref.
 */
export const useAsyncValidator = (
  value: Ref<string>,
  validatorFunc: (v: string) => Promise<RequestResponse<ValidationResponse>>,
  validatorMessage: string,
  errorMessages: Ref<string[]>
) => {
  const valid = ref(false);

  const validate = async () => {
    errorMessages.value = [];
    const { data } = await validatorFunc(value.value);

    if (!data?.valid) {
      valid.value = false;
      errorMessages.value.push(validatorMessage);
      return;
    }

    valid.value = true;
  };

  return { validate, valid };
};
