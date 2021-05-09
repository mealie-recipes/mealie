export const initials = {
  computed: {
    initials() {
      if (!this.user.fullName) return "00"
      const allNames = this.user.fullName.trim().split(" ");
      const initials = allNames.reduce(
        (acc, curr, index) => {
          if (index === 0 || index === allNames.length - 1) {
            acc = `${acc}${curr.charAt(0).toUpperCase()}`;
          }
          return acc;
        },
        [""]
      );
      return initials;
    },
  },
};
