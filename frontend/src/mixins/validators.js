export const validators = {
  data() {
    return {
      emailRule: v =>
        !v ||
        /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(v) ||
        "E-mail must be valid",

      existsRule: value => !!value || "Field Required",

      minRule: v =>
        v.length >= 8 || "Use 8 characters or more for your password",
    };
  },
};
