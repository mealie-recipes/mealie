import { computed, ComputedRef, Ref } from "@nuxtjs/composition-api";

const EMAIL_REGEX =
  /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@(([[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

const URL_REGEX = /[-a-zA-Z0-9@:%._+~#=]{1,256}.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)/;

export const validators: { [key: string]: (v: string) => boolean | string } = {
  required: (v: string) => !!v || "This Field is Required",
  email: (v: string) => !v || EMAIL_REGEX.test(v) || "Email Must Be Valid",
  whitespace: (v: string) => !v || v.split(" ").length <= 1 || "No Whitespace Allowed",
  url: (v: string) => !v || URL_REGEX.test(v) || "Must Be A Valid URL",
  // TODO These appear to be unused?
  // minLength: (min: number) => (v: string) => !v || v.length >= min || `Must Be At Least ${min} Characters`,
  // maxLength: (max: number) => (v: string) => !v || v.length <= max || `Must Be At Most ${max} Characters`,
};

const hasOneUpperCase = (v: string) => /[A-Z]/.test(v);
const hasOneLowerCase = (v: string) => /[a-z]/.test(v);
const hasOneNumber = (v: string) => /[0-9]/.test(v);
const hasSpecialCharacter = (v: string) => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(v);

export interface PasswordRequirement {
  label: string;
  met: ComputedRef<boolean>;
}

export const usePasswordValidator = (password: Ref<string>) => {
  const validatorLengthText = "Password must be at least 8 characters";
  const validatorLengthTextFunc = (v: string) => (!!v && v.length >= 8) || validatorLengthText;
  const validatorLength = {
    label: validatorLengthText,
    met: computed(() => validatorLengthTextFunc(password.value) === true),
  };

  const validatorUpperCaseText = "Password must contain at least one uppercase letter";
  const validatorUpperCaseFunc = (v: string) => (!!v && hasOneUpperCase(v)) || validatorUpperCaseText;
  const validatorUpperCase = {
    label: validatorUpperCaseText,
    met: computed(() => validatorUpperCaseFunc(password.value) === true),
  };

  const validatorLowerCaseText = "Password must contain at least one lowercase letter";
  const validatorLowerCaseFunc = (v: string) => (!!v && hasOneLowerCase(v)) || validatorLowerCaseText;
  const validatorLowerCase = {
    label: validatorLowerCaseText,
    met: computed(() => validatorLowerCaseFunc(password.value) === true),
  };

  const validateSpecialCharacterText = "Password contain at least one special character";
  const validateSpecialCharacterFunc = (v: string) => (!!v && hasSpecialCharacter(v)) || validateSpecialCharacterText;
  const validateSpecialCharacter = {
    label: validateSpecialCharacterText,
    met: computed(() => validateSpecialCharacterFunc(password.value) === true),
  };

  const validateNumberText = "Password must contain at least one number";
  const validateNumberFunc = (v: string) => (!!v && hasOneNumber(v)) || validateNumberText;
  const validateNumber = {
    label: validateNumberText,
    met: computed(() => validateNumberFunc(password.value) === true),
  };

  const passwordValidators = [
    validatorLengthTextFunc,
    validatorUpperCaseFunc,
    validatorLowerCaseFunc,
    validateSpecialCharacterFunc,
    validateNumberFunc,
  ];

  const isValid = computed(() => {
    return passwordValidators.every((v) => v(password.value) === true);
  });

  return {
    isValid,
    passwordValidators,
    validatorLength,
    validatorUpperCase,
    validatorLowerCase,
    validateSpecialCharacter,
    validateNumber,
  };
};
