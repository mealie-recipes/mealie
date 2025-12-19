"use client";

import { useEffect, useState } from "react";
import { fetchAppConfig, fetchStartupInfo } from "@/lib/api/app";
import type { AppConfig, StartupInfo } from "@/lib/types/app";
import Loader from "@/components/ui/custom/loader";
import BasicError from "@/components/ui/custom/basic-error";
import { Button } from "@/components/ui/button";
import { RegistrationForm } from "@/components/ui/auth/registration-form";

export default function RegistrationPage() {
  const [startupInfo, setStartupInfo] = useState<StartupInfo | null>(null);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadConfig() {
      try {
        const startupInfo = await fetchStartupInfo();
        setStartupInfo(startupInfo);
        const appConfig = await fetchAppConfig();
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
