import { recipe } from "@/utils/recipe";
import { store } from "@/store";

// TODO: Migrate to Mixins

export const utils = {
  recipe,
  generateUniqueKey(item, index) {
    return `${item}-${index}`;
  },
  getDateAsPythonDate(dateObject) {
    if (!dateObject) return null;
    const month = dateObject.getMonth() + 1;
    const day = dateObject.getDate();
    const year = dateObject.getFullYear();
    return `${year}-${month}-${day}`;
  },
  notify: {
    info(text, title = null) {
      store.commit("setSnackbar", {
        open: true,
        title,
        text,
        color: "info",
      });
    },
    success(text, title = null) {
      store.commit("setSnackbar", {
        open: true,
        title,
        text,
        color: "success",
      });
    },
    error(text, title = null) {
      store.commit("setSnackbar", {
        open: true,
        title,
        text,
        color: "error",
      });
    },
    warning(text, title = null) {
      store.commit("setSnackbar", {
        open: true,
        title,
        text,
        color: "warning",
      });
    },
  },
};
