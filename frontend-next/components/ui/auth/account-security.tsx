"use client";

import { Button } from "@/components/ui/button";
import { PasswordInput } from "@/components/ui/password-input";
import { Label } from "@/components/ui/label";
import { PasswordStrength } from "./password-strength";
import { useRegistration } from "./registration-context";

/**
 * Render the account security step with password and confirm-password inputs, live validation, strength indicator, and navigation controls.
 *
 * Displays an error when the passwords are non-empty and do not match, shows password strength for the current password, and enables the Continue action only when the password is at least 8 characters and matches the confirmation.
 *
 * @returns The component's UI as a JSX element
 */
export function AccountSecurity() {
  const { data, updateData, goBack, goNext } = useRegistration();

  const password = data.password || "";
  const confirmPassword = data.confirmPassword || "";

  const passwordsMatch = password === confirmPassword;
  const showMatchError =
    password &&
    confirmPassword &&
    !passwordsMatch &&
    confirmPassword.length > 0;

  const isValid = password.length >= 8 && passwordsMatch;

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300 mx-auto max-w-[270px] sm:max-w-[325px]">
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <PasswordInput
            id="password"
            value={password}
            onChange={(e) => updateData({ password: e.target.value })}
          />
        </div>
        <div className="space-y-2 relative">
          <Label htmlFor="confirm-password">Confirm Password</Label>
          <PasswordInput
            id="confirm-password"
            value={confirmPassword}
            onChange={(e) => updateData({ confirmPassword: e.target.value })}
            aria-invalid={!!showMatchError}
          />
          <div className="absolute top-full right-0 pt-1">
            {showMatchError && (
              <p className="text-xs text-destructive text-right">
                Passwords do not match
              </p>
            )}
          </div>
        </div>
        <div className="pt-2">
          <PasswordStrength password={password} />
        </div>
      </div>
      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={goBack} className="">
          Back
        </Button>
        <Button disabled={!isValid} onClick={goNext}>
          Continue
        </Button>
      </div>
    </div>
  );
}
