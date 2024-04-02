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
      if (this.token.get()) {
        this.token.reset();
      }
      const redirect = await super._handleCallback()
      await this.updateAccessToken()

      // eslint-disable-next-line @typescript-eslint/no-unsafe-return
      return redirect;
    }

    async updateAccessToken() {
      if (!this.idToken.sync()) {
        return
      }
      if (this.isValidMealieToken()) {
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
