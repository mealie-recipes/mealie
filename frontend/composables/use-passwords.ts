import { computed, Ref, ref, useContext } from "@nuxtjs/composition-api";
import { scorePassword } from "~/lib/validators";

export function usePasswordField() {
  const show = ref(false);

  const { $globals } = useContext();

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

export const usePasswordStrength = (password: Ref<string>) => {
  const score = computed(() => {
    return scorePassword(password.value);
  });

  const strength = computed(() => {
    if (score.value < 50) {
      return "Weak";
    } else if (score.value < 80) {
      return "Good";
    } else if (score.value < 100) {
      return "Strong";
    } else {
      return "Very Strong";
    }
  });

  const color = computed(() => {
    if (score.value < 50) {
      return "error";
    } else if (score.value < 80) {
      return "warning";
    } else if (score.value < 100) {
      return "info";
    } else {
      return "success";
    }
  });

  return { score, strength, color };
};
