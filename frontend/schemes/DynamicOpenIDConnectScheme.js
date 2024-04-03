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
    // Differences are, we don't check if the id token is valid because we only use it on the initial
    // log in sequence to check for identity, so if it's expired but we have a valid access token, then its fine
    check(checkStatus = false) {
      const response = {
        valid: false,
        tokenExpired: false,
        refreshTokenExpired: false,
        idTokenExpired: false,
        isRefreshable: true
      }

      // Sync tokens
      const token = this.token.sync()
      this.refreshToken.sync()

      // Token is required but not available
      if (!token) {
        return response
      }

      // Check status wasn't enabled, let it pass
      if (!checkStatus) {
        response.valid = true
        return response
      }

      // Get status
      const tokenStatus = this.token.status()
      const refreshTokenStatus = this.refreshToken.status()

      // Refresh token has expired. There is no way to refresh. Force reset.
      if (refreshTokenStatus.expired()) {
        console.log("refresh token expired")
        response.refreshTokenExpired = true
        return response
      }

      // Token has expired, Force reset.
      if (tokenStatus.expired()) {
        console.log("token expired")
        response.tokenExpired = true
        return response
      }

      response.valid = true
      return response
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
      } catch {
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
