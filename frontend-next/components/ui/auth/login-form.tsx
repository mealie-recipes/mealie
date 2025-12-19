"use client";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { PasswordInput } from "@/components/ui/password-input";
import { Badge } from "../badge";
import { Alert, AlertTitle, AlertDescription } from "../alert";
import { AlertCircle, Loader2 } from "lucide-react";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { AppConfig, StartupInfo } from "@/lib/types/app";
import { CredentialRow } from "../custom/auth/credential-row";
import BasicError from "../custom/basic-error";

interface LoginFormProps extends React.ComponentProps<"div"> {
  config: AppConfig;
  startupInfo: StartupInfo;
}

/**
 * Render the sign-in UI and handle password and OIDC authentication flows.
 *
 * This component displays password and/or OIDC login options based on the provided configuration,
 * shows first-login and error alerts when applicable, and performs navigation on successful sign-in.
 *
 * @param config - Application configuration controlling available login methods and UI flags (e.g., demoStatus, enableOidc, allowPasswordLogin, allowSignup, oidcProviderName).
 * @param startupInfo - Startup information used to determine first-login alerts and related UI.
 * @returns The React element for the login form.
 */
export function LoginForm({
  className,
  config,
  startupInfo,
  ...props
}: LoginFormProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [password, setPassword] = useState("");

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const submittedPassword = password.trim();
      if (!submittedPassword) {
        throw new Error("Password cannot be empty");
      }
      // TODO: Implement actual login API call
      // Placeholder for actual authentication
      await new Promise((resolve) => setTimeout(resolve, 1000));
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOidcLogin = () => {
    // Use window.location.href for OIDC as it requires full page redirect to IdP
    window.location.href = "/api/auth/oidc/login";
  };

  if (!config.allowPasswordLogin && !config.enableOidc) {
    return (
      <BasicError error="No login methods are enabled. Please contact the administrator." />
    );
  }

  return (
    <div className="flex items-center justify-center">
      <Card
        className={cn(
          "w-[320px] sm:w-[375px] sm:min-w-[375px]",
          config.demoStatus ? "pt-0" : ""
        )}
      >
        {config.demoStatus && (
          <div className="bg-primary px-4 py-3 text-center text-sm font-bold text-white">
            Demo Mode Active
          </div>
        )}
        <CardHeader className="justify-center items-center text-center p-2">
          <CardTitle>Welcome</CardTitle>
          <CardDescription>Sign in to your account</CardDescription>
          {startupInfo.isFirstLogin && (
            <Alert variant="info" className="mt-2">
              <AlertCircle />
              <div className="flex flex-col">
                <AlertTitle>
                  It looks like this is your first time logging in.
                </AlertTitle>
                <AlertDescription>
                  Don't want to see this anymore? Be sure to change your email
                  in your user settings!
                </AlertDescription>
                <div className="flex flex-col gap-2 mt-4">
                  <CredentialRow
                    label="Username"
                    value="changeme@example.com"
                  />
                  <CredentialRow
                    label="Password"
                    value="MyPassword"
                    isPassword
                  />
                </div>
              </div>
            </Alert>
          )}
          {error && (
            <Alert variant="destructive" className="mt-2">
              <AlertCircle />
              <div className="flex flex-col">
                <AlertTitle>Login Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </div>
            </Alert>
          )}
        </CardHeader>
        <CardContent>
          {config.allowPasswordLogin && (
            <form onSubmit={handlePasswordLogin}>
              <FieldGroup>
                <Field>
                  <FieldLabel htmlFor="email">Email or Username</FieldLabel>
                  <Input
                    id="email"
                    type="text"
                    autoComplete="username"
                    placeholder="name@company.com"
                    required
                  />
                </Field>
                <Field>
                  <div className="flex items-center">
                    <FieldLabel htmlFor="password">Password</FieldLabel>
                    <a
                      href="#"
                      className="ml-auto inline-block text-xs underline-offset-4 hover:underline text-primary"
                    >
                      Forgot your password?
                    </a>
                  </div>
                  <PasswordInput
                    id="password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                  <div className="flex items-center gap-2">
                    <Checkbox id="remember" />
                    <FieldLabel htmlFor="remember">Remember me</FieldLabel>
                  </div>
                </Field>
                <Field>
                  <Button type="submit" disabled={isSubmitting}>
                    <span>{isSubmitting ? <Loader2 /> : "Login"}</span>
                  </Button>

                  {/* If Allowed sign up */}
                  {config.allowSignup ? (
                    <FieldDescription className="text-center pt-2">
                      Don&apos;t have an account?{" "}
                      <a
                        href="/register"
                        className="no-underline hover:underline text-primary"
                      >
                        Sign up
                      </a>
                    </FieldDescription>
                  ) : (
                    <FieldDescription className="text-center">
                      Don&apos;t have an account?
                      <Badge variant="secondary" className="ml-2">
                        Invite Only
                      </Badge>
                    </FieldDescription>
                  )}
                </Field>
              </FieldGroup>
            </form>
          )}
          {config.allowPasswordLogin && config.enableOidc && (
            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-zinc-300 dark:border-zinc-600"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-card px-2 text-zinc-500 dark:text-zinc-400">
                  OR
                </span>
              </div>
            </div>
          )}
          {config.enableOidc && (
            <div className="flex items-center w-full justify-center">
              <Button
                variant="outline"
                type="button"
                className="w-full"
                disabled={isSubmitting}
                onClick={handleOidcLogin}
              >
                <span>
                  {isSubmitting ? <Loader2 /> : "Login with "}
                  {config.oidcProviderName || "SSO"}
                </span>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
