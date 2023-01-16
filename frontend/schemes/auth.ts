import { HTTPResponse } from "@nuxtjs/auth-next";
import { LocalScheme } from "~auth/runtime"

export default class Auth extends LocalScheme {
  async mounted(): Promise<HTTPResponse | void> {
    // nuxt-auth can't be configured from the environment directly, so we
    // overwrite redirect.logout here
    if (this.$auth.ctx.$config.SSO_LOGOUT_URL !== null) {
      this.$auth.options.redirect.logout = this.$auth.ctx.$config.SSO_LOGOUT_URL;
    }

    return await super.mounted();
  }
}
