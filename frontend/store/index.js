export const store = {};

export const state = () => ({
  ssoUser: null
})

export const mutations = {
  set_sso_user(state, user) {
    state.ssoUser = user
  }
}

export const actions = {
  async nuxtServerInit({ commit }, { req, $config }) {
    let trustedHeader = $config.SSO_TRUSTED_HEADER_USER;
    if (trustedHeader !== null) {
      // req.headers has lower-cased keys
      trustedHeader = trustedHeader.toLowerCase();

      if (req.headers && req.headers[trustedHeader]) {
        await commit("set_sso_user", req.headers[trustedHeader]);
      }
    }
  }
}
