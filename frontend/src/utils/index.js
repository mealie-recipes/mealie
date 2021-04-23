import { vueApp } from "../main";

// TODO: Migrate to Mixins
const notifyHelpers = {
  baseCSS: "notify-base",
  error: "notify-error-color",
  warning: "notify-warning-color",
  success: "notify-success-color",
  info: "notify-info-color",
};

export default {
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
    show: function(text, type = "info", title = null) {
      vueApp.flashMessage.show({
        status: type,
        title: title,
        message: text,
        time: 3000,
        blockClass: `${notifyHelpers.baseCSS} ${notifyHelpers[type]}`,
        contentClass: `${notifyHelpers.baseCSS} ${notifyHelpers[type]}`,
      });
    },
    info: function(text, title = null) {
      this.show(text, "info", title);
    },
    success: function(text, title = null) {
      this.show(text, "success", title);
    },
    error: function(text, title = null) {
      this.show(text, "error", title);
    },
    warning: function(text, title = null) {
      this.show(text, "warning", title);
    },
  },
};
