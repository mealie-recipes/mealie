import { icons } from "~/lib/icons";

export default defineNuxtPlugin(() => {
  return {
    provide: {
      globals: {
        icons,
      },
    },
  };
});
