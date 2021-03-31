import { api } from "@/api";

const state = {
  groups: [],
  currentGroup: {},
};

const mutations = {
  setGroups(state, payload) {
    state.groups = payload;
  },
  setCurrentGroup(state, payload) {
    state.currentGroup = payload;
  },
};

const actions = {
  async requestAllGroups({ commit }) {
    const groups = await api.groups.allGroups();
    commit("setGroups", groups);
  },
  async requestCurrentGroup({ commit }) {
    const group = await api.groups.current();
    commit("setCurrentGroup", group);
  },
};

const getters = {
  getGroups: state => state.groups,
  getGroupNames: state => Array.from(state.groups, x => x.name),
  getCurrentGroup: state => state.currentGroup,
};

export default {
  state,
  mutations,
  actions,
  getters,
};
