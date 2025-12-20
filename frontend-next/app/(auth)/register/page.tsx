"use client";

import { useEffect, useState } from "react";
import type { AppConfig, StartupInfo } from "@/lib/types/app";
import Loader from "@/components/ui/custom/loader";
import BasicError from "@/components/ui/custom/basic-error";
import { Button } from "@/components/ui/button";
import { RegistrationForm } from "@/components/ui/auth/registration-form";
import { configApi } from "@/lib/api/public/config";

/**
 * Display the registration page and manage initial configuration loading, error states, and OIDC redirect.
 *
 * When mounted, the component loads startup information and app configuration, shows a loader while fetching,
 * renders user-facing error views if loading fails, automatically performs a full-page redirect to the OIDC
 * login endpoint when OIDC is enabled and `oidcRedirect` is true, and otherwise either shows a registration-disabled
 * message with a login button or renders the registration form with the loaded configuration.
 *
 * @returns A React element for the registration page.
 */
export default function RegistrationPage() {
  const [startupInfo, setStartupInfo] = useState<StartupInfo | null>(null);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    /**
     * Load startup information and application configuration into component state,
     * perform an OIDC full-page redirect when configured, and update loading/error state.
     *
     * Sets the component's startupInfo and config state values on success. If the
     * fetched app config enables OIDC and requests a redirect, navigates the browser
     * to /api/auth/oidc/login. On failure, sets an error message; in all cases,
     * clears the loading flag when finished.
     */
    async function loadConfig() {
      try {
        const startupInfo = await configApi.getStartupInfo();
        setStartupInfo(startupInfo);
        const appConfig = await configApi.getAppConfig();
        setConfig(appConfig);

        // Auto-redirect to OIDC if enabled and redirect is true
        if (appConfig.enableOidc && appConfig.oidcRedirect) {
          // Use window.location.href for OIDC as it requires full page redirect to IdP
          window.location.href = "/api/auth/oidc/login";
          return;
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load configuration"
        );
      } finally {
        setLoading(false);
      }
    }

    loadConfig();
  }, []);

  if (loading) {
    return <Loader />;
  }

  if (!config) {
    return (
      <BasicError error={error || "Failed to load application configuration"} />
    );
  }

  if (!startupInfo) {
    return <BasicError error={error || "Failed to load Database"} />;
  }

  if (config.allowSignup === false) {
    return (
      <div>
        <BasicError error="Registrations are disabled. Please contact the administrator." />
        {/* Login Button */}
        <div className="mt-4 w-full flex justify-center">
          <Button
            variant="outline"
            type="button"
            onClick={() => (window.location.href = "/login")}
          >
            Go to Login
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      <RegistrationForm config={config} />
    </>
  );
}