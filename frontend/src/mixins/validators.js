const EMAIL_REGEX = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@(([[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

export const validators = {
  data() {
    return {
      emailRule: v => !v || EMAIL_REGEX.test(v) || this.$t("user.e-mail-must-be-valid"),

      existsRule: value => !!value || this.$t("general.field-required"),

      minRule: v => v.length >= 8 || this.$t("user.use-8-characters-or-more-for-your-password"),

      whiteSpace: v => !v || v.split(" ").length <= 1 || this.$t("recipe.no-white-space-allowed"),
    };
  },
};
