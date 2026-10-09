package io.mealie.backend.app;

import java.util.List;

/** Public application settings returned by Python's {@code /api/app/about}. */
public record AppInfo(
        boolean production,
        String version,
        boolean demoStatus,
        boolean allowSignup,
        boolean allowPasswordLogin,
        String defaultGroupSlug,
        String defaultHouseholdSlug,
        boolean enableOidc,
        boolean oidcRedirect,
        String oidcProviderName,
        int tokenTime,
        List<String> allowedIframeHosts) {
}
