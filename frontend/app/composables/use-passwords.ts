import { computed } from "vue";
import type { VueI18n } from "vue-i18n";
import { scorePassword } from "~/lib/validators";

export function usePasswordField() {
  const show = ref(false);
  const { $globals } = useNuxtApp();

  const passwordIcon = computed(() => {
    return show.value ? $globals.icons.eyeOff : $globals.icons.eye;
  });
  const inputType = computed(() => (show.value ? "text" : "password"));

  const togglePasswordShow = () => {
    show.value = !show.value;
  };

  return {
    inputType,
    togglePasswordShow,
    passwordIcon,
  };
}

export const usePasswordStrength = (password: Ref<string>, i18n: VueI18n) => {
  const score = computed(() => scorePassword(password.value));
  const strength = computed(() => {
    if (score.value < 50) {
      return i18n.t("user.password-strength-values.weak");
    }
    else if (score.value < 80) {
      return i18n.t("user.password-strength-values.good");
    }
    else if (score.value < 100) {
      return i18n.t("user.password-strength-values.strong");
    }
    else {
      return i18n.t("user.password-strength-values.very-strong");
    }
  });

  const color = computed(() => {
    if (score.value < 50) {
      return "error";
    }
    else if (score.value < 80) {
      return "warning";
    }
    else if (score.value < 100) {
      return "info";
    }
    else {
      return "success";
    }
  });

  return { score, strength, color };
};
