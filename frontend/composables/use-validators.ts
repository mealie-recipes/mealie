const EMAIL_REGEX =
  /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@(([[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/

const URL_REGEX = /^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,256}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$/gm;

export const validators = {
  required: (v: string) => !!v || "This Field is Required",
  email: (v: string) => !v || EMAIL_REGEX.test(v) || "Email Must Be Valid",
  whitespace: (v: string) => !v || v.split(" ").length <= 1 || "No Whitespace Allowed",
  url: (v: string) => !v || URL_REGEX.test(v) || "Must Be A Valid URL",
}
