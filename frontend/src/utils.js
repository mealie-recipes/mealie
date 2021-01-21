// import utils from "../../utils";
// import Vue from "vue";
// import Vuetify from "./plugins/vuetify";

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
    return `/api/recipe/image/${image}/`;
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
};
