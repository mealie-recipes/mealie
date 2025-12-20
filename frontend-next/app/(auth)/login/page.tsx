"use client";

import { useEffect, useState } from "react";
import type { AppConfig, StartupInfo } from "@/lib/types/app";
import { LoginForm } from "@/components/ui/auth/login-form";
import { ProjectLinks } from "@/components/ui/custom/auth/project-links";
import Loader from "@/components/ui/custom/loader";
import BasicError from "@/components/ui/custom/basic-error";
import { useAuth } from "@/lib/auth/auth-context";
import { useRouter } from "next/navigation";
import { configApi } from "@/lib/api/public/config";

/**
 * Renders the login page: loads startup info and app configuration, displays a loader while fetching, shows errors when loading fails, and renders the login form and footer when successful.
 *
 * If the fetched configuration enables OIDC and requests a redirect, performs a full-page redirect to /api/auth/oidc/login.
 *
 * @returns The React element for the login page.
 */
export default function LoginPage() {
  const router = useRouter();
  const [startupInfo, setStartupInfo] = useState<StartupInfo | null>(null);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { loggedIn } = useAuth();

  useEffect(() => {
    if (loggedIn) {
      router.push("/");
      return;
    }

    /**
     * Loads startup information and application configuration, updating component state.
     *
     * Retrieves startup info and app config, stores them in component state, and if OIDC login is enabled with redirect requested, performs a full-page redirect to /api/auth/oidc/login. On failure, records an error message. In all cases, clears the loading indicator when finished.
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
  }, [loggedIn, router]);

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

  return (
    <>
      <LoginForm config={config} startupInfo={startupInfo} />

      {/* Footer */}
      <div className="mt-8 flex flex-col gap-6 text-center font-mono text-xs text-zinc-500 dark:text-zinc-500">
        <ProjectLinks />
        {config.version && (
          <p className="font-mono text-xs">Version {config.version}</p>
        )}
      </div>
    </>
  );
}