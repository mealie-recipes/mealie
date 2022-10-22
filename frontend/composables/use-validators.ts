import { ref, Ref } from "@nuxtjs/composition-api";
import { RequestResponse } from "~/lib/api/types/non-generated";
import { ValidationResponse } from "~/lib/api/types/response";
import { required, email, whitespace, url, minLength, maxLength } from "~/lib/validators";

export const validators = {
  required,
  email,
  whitespace,
  url,
  minLength,
  maxLength,
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
