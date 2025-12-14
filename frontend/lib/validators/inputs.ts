import { useGlobalI18n } from "~/composables/use-global-i18n";

const EMAIL_REGEX
  = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@(([[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

const URL_REGEX = /[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)/;

export function required(v: string | undefined | null) {
  const i18n = useGlobalI18n();
  return !!v || i18n.t("validators.required");
}

export function email(v: string | undefined | null) {
  const i18n = useGlobalI18n();
  return (!!v && EMAIL_REGEX.test(v)) || i18n.t("validators.invalid-email");
}

export function whitespace(v: string | null | undefined) {
  const i18n = useGlobalI18n();
  return (!!v && v.split(" ").length <= 1) || i18n.t("validators.no-whitespace");
}

export function url(v: string | undefined | null) {
  const i18n = useGlobalI18n();
  return (!!v && URL_REGEX.test(v)) || i18n.t("validators.invalid-url");
}

export function urlOptional(v: string | undefined | null) {
  return v ? url(v) : true;
}

export function minLength(min: number) {
  const i18n = useGlobalI18n();
  return (v: string | undefined | null) => (!!v && v.length >= min) || i18n.t("validators.min-length", { min });
}

export function maxLength(max: number) {
  const i18n = useGlobalI18n();
  return (v: string | undefined | null) => !v || v.length <= max || i18n.t("validators.max-length", { max });
}
