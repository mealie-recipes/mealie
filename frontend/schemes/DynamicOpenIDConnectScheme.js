import jwtDecode from "jwt-decode"
import { ConfigurationDocument, OpenIDConnectScheme } from "~auth/runtime"

/**
 * Custom Scheme that dynamically gets the OpenID Connect configuration from the backend.
 * This is needed because the SPA frontend does not have access to runtime environment variables.
 */
export default class DynamicOpenIDConnectScheme extends OpenIDConnectScheme {

    async mounted() {
        await this.getConfiguration();
        this.options.scope = ["openid", "profile", "email", "groups"]

        this.configurationDocument = new ConfigurationDocument(
            this,
            this.$auth.$storage
        )

        // eslint-disable-next-line @typescript-eslint/no-unsafe-return
        return await super.mounted()
    }

    // Overrides the check method in the OpenIDConnectScheme
    // We don't care if the id token is expired as long as we have a valid Mealie token.
    // We only use the id token to verify identity on the initial login, then issue a Mealie token
    check(checkStatus = false) {
      const response = super.check(checkStatus)

      // we can do this because id token is the last thing to be checked so if the id token is expired then it was
      // the only thing making the request not valid
      if (response.idTokenExpired && !response.valid) {
        response.valid = true;
        response.idTokenExpired = false;
      }
      // eslint-disable-next-line @typescript-eslint/no-unsafe-return
      return response;
    }

    async fetchUser() {
      if (!this.check().valid) {
        return
      }

      const { data } = await this.$auth.requestWith(this.name, {
        url: "/api/users/self"
      })

      this.$auth.setUser(data)
    }

    async _handleCallback() {
      // sometimes the mealie token is being sent in the request to the IdP on callback which
      // causes an error, so we clear it if we have one
      if (!this.token.status().valid()) {
        this.token.reset();
      }
      const redirect = await super._handleCallback()
      await this.updateAccessToken()

      // eslint-disable-next-line @typescript-eslint/no-unsafe-return
      return redirect;
    }

    async updateAccessToken() {
      if (this.isValidMealieToken()) {
        return
      }
      if (!this.idToken.status().valid()) {
        this.idToken.reset();
        return
      }

      try {
        const response = await this.$auth.requestWith(this.name, {
          url: "/api/auth/token",
          method: "post"
        })
        // Update tokens with mealie token
        this.updateTokens(response)
      } catch (e) {
        if (e.response?.status === 401) {
          this.$auth.reset()
        }
        const currentUrl = new URL(window.location.href)
        if (currentUrl.pathname === "/login" && currentUrl.searchParams.has("direct")) {
          return
        }
        window.location.replace("/login?direct=1")
      }
    }

    isValidMealieToken() {
      if (this.token.status().valid()) {
        let iss = null;
        try {
          // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
          iss = jwtDecode(this.token.get()).iss
        } catch (e) {
          // pass
        }
        return iss === "mealie"
      }
      return false
    }

    async getConfiguration() {
        const route = "/api/app/about/oidc";

        try {
            const response = await fetch(route);
            const data = await response.json();
            this.options.endpoints.configuration = data.configurationUrl;
            this.options.clientId = data.clientId;
        } catch (error) {
            // pass
        }
    }
}
