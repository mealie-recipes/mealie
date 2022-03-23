import { computed, ref, useContext } from "@nuxtjs/composition-api";

export function usePasswordField() {
  const show = ref(false);

  const { $globals } = useContext();

  const passwordIcon = computed(() => {
    return show ? $globals.icons.eyeOff : $globals.icons.eye;
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
