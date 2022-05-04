import { computed, Ref, ref, useContext } from "@nuxtjs/composition-api";

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

function scorePassword(pass: string): number {
  let score = 0;
  if (!pass) return score;

  const flaggedWords = ["password", "mealie", "admin", "qwerty", "login"];

  if (pass.length < 6) return score;

  // Check for flagged words
  for (const word of flaggedWords) {
    if (pass.toLowerCase().includes(word)) {
      score -= 100;
    }
  }

  // award every unique letter until 5 repetitions
  const letters: { [key: string]: number } = {};

  for (let i = 0; i < pass.length; i++) {
    letters[pass[i]] = (letters[pass[i]] || 0) + 1;
    score += 5.0 / letters[pass[i]];
  }

  // bonus points for mixing it up
  const variations: { [key: string]: boolean } = {
    digits: /\d/.test(pass),
    lower: /[a-z]/.test(pass),
    upper: /[A-Z]/.test(pass),
    nonWords: /\W/.test(pass),
  };

  let variationCount = 0;
  for (const check in variations) {
    variationCount += variations[check] === true ? 1 : 0;
  }
  score += (variationCount - 1) * 10;

  return score;
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
