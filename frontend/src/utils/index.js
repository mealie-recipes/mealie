import { recipe } from "@/utils/recipe";
import { store } from "@/store";

// TODO: Migrate to Mixins

export const utils = {
  recipe: recipe,
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
  copyToClipboard(textToCopy) {
    // navigator clipboard api needs a secure context (https)
    if (navigator.clipboard && window.isSecureContext) {
      // navigator clipboard api method'
      return navigator.clipboard.writeText(textToCopy);
    } else {
      // text area method
      let textArea = document.createElement("textarea");
      textArea.value = textToCopy;
      // make the textarea out of viewport
      textArea.style.position = "fixed";
      textArea.style.left = "-999999px";
      textArea.style.top = "-999999px";
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      return new Promise((res, rej) => {
        // here the magic happens
        document.execCommand("copy") ? res() : rej();
        textArea.remove();
      });
    }
  },
};
