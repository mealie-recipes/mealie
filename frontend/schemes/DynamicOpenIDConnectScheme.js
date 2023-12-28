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

      await this.updateAccessToken()
      const { data } = await this.$auth.requestWith(this.name, {
        url: "/api/users/self"
      })

      this.$auth.setUser(data)
    }

    async updateAccessToken() {
      const response = await this.$auth.requestWith(this.name, {
        url: "/api/auth/token",
        method: "post"
      })

      // Update tokens with mealie token
      this.updateTokens(response)
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
