export const utilMixins = {
  commputed: {
    isMobile() {
      return this.$vuetify.breakpoint.name === "xs";
    },
  },
};
