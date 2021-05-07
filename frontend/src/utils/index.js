import { recipe } from "@/utils/recipe";
import { store } from "@/store";

// TODO: Migrate to Mixins

export const utils = {
  recipe: recipe,
  getImageURL(image) {
    return `/api/recipes/${image}/image?image_type=small`;
  },
  generateUniqueKey(item, index) {
    const uniqueKey = `${item}-${index}`;
    return uniqueKey;
  },
  getDateAsPythonDate(dateObject) {
    const month = dateObject.getUTCMonth() + 1;
    const day = dateObject.getUTCDate();
    const year = dateObject.getFullYear();

    return `${year}-${month}-${day}`;
  },
  notify: {
    info: function(text, title = null) {
      store.commit("setSnackbar", {
        open: true,
        title: title,
        text: text,
        color: "info",
      });
    },
    success: function(text, title = null) {
      store.commit("setSnackbar", {
        open: true,
        title: title,
        text: text,
        color: "success",
      });
    },
    error: function(text, title = null) {
      store.commit("setSnackbar", {
        open: true,
        title: title,
        text: text,
        color: "error",
      });
    },
    warning: function(text, title = null) {
      store.commit("setSnackbar", {
        open: true,
        title: title,
        text: text,
        color: "warning",
      });
    },
  },
};
