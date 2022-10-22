const EMAIL_REGEX =
  /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@(([[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

const URL_REGEX = /[-a-zA-Z0-9@:%._+~#=]{1,256}.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)/;

export function required(v: string | undefined | null) {
  return !!v || "This Field is Required";
}

export function email(v: string | undefined | null) {
  return (!!v && EMAIL_REGEX.test(v)) || "Email Must Be Valid";
}

export function whitespace(v: string | null | undefined) {
  return (!!v && v.split(" ").length <= 1) || "No Whitespace Allowed";
}

export function url(v: string | undefined | null) {
  return (!!v && URL_REGEX.test(v)) || "Must Be A Valid URL";
}

export function minLength(min: number) {
  return (v: string | undefined | null) => (!!v && v.length >= min) || `Must Be At Least ${min} Characters`;
}

export function maxLength(max: number) {
  return (v: string | undefined | null) => !v || v.length <= max || `Must Be At Most ${max} Characters`;
}
