import { ConfigurationDocument, OpenIDConnectScheme } from "~auth/runtime"

/**
 * Custom Scheme that dynamically gets the OpenID Connect configuration from the backend.
 * This is needed because the SPA frontend does not have access to runtime environment variables.
 */
export default class DynamicOpenIDConnectScheme extends OpenIDConnectScheme {

    async mounted() {
        await this.setConfiguration();
        this.options.scope = ["openid", "profile", "email"]

        this.configurationDocument = new ConfigurationDocument(
            this,
            this.$auth.$storage
        )


        // eslint-disable-next-line @typescript-eslint/no-unsafe-return
        return super.mounted()
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

    async setConfiguration() {
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
