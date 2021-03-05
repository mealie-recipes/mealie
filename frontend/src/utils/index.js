import { vueApp } from "../main";

// TODO: Migrate to Mixins
const notifyHelpers = {
  baseCSS: "notify-base",
  error: "notify-error-color",
  warning: "notify-warning-color",
  success: "notify-success-color",
  info: "notify-info-color",
};

const days = [
  "Sunday",
  "Monday",
  "Tueday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];
const months = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

const monthsShort = [
  "Jan",
  "Feb",
  "March",
  "April",
  "May",
  "June",
  "July",
  "Aug",
  "Sept",
  "Oct",
  "Nov",
  "Dec",
];

export default {
  getImageURL(image) {
    return `/api/recipes/${image}/image`;
  },
  generateUniqueKey(item, index) {
    const uniqueKey = `${item}-${index}`;
    return uniqueKey;
  },
  getDateAsText(dateObject) {
    const dow = days[dateObject.getUTCDay()];
    const month = months[dateObject.getUTCMonth()];
    const day = dateObject.getUTCDate();
    // const year = dateObject.getFullYear();

    return `${dow}, ${month} ${day}`;
  },
  getDateAsTextAlt(dateObject) {
    const dow = days[dateObject.getUTCDay()];
    const month = monthsShort[dateObject.getUTCMonth()];
    const day = dateObject.getUTCDate();
    // const year = dateObject.getFullYear();

    return `${dow}, ${month} ${day}`;
  },
  getDateAsPythonDate(dateObject) {
    const month = dateObject.getMonth() + 1;
    const day = dateObject.getDate();
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
