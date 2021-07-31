const state = {
  snackbar: {
    open: false,
    text: "Hello From The Store",
    color: "info",
  },
};

const mutations = {
  setSnackbar(state, payload) {
    state.snackbar = payload;
  },
};

const getters = {
  getSnackbar: state => state.snackbar,
};

export default {
  state,
  mutations,
  getters,
};
