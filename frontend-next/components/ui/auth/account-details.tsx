"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { useRegistration } from "./registration-context";

/**
 * Render an account details form with inputs for full name, username, and email plus Back and Continue controls.
 *
 * The component validates that full name is present and surface username/email validation states (checking, errors, availability).
 * The Continue control is disabled until the full name is provided and username/email pass their validations.
 *
 * @returns The component's rendered JSX element for the account details step
 */
export function AccountDetails() {
  const { data, updateData, goBack, goNext, validations } = useRegistration();
  const { username, email } = validations;

  const [fullNameError, setFullNameError] = useState<string | null>(null);

  const handleFullNameBlur = () => {
    if (!data.fullName?.trim()) {
      setFullNameError("Full name is required");
    } else {
      setFullNameError(null);
    }
  };

  const handleContinue = () => {
    if (!data.fullName?.trim()) {
      setFullNameError("Full name is required");
      return;
    }

    if (username.error || email.error || fullNameError) {
      return;
    }

    if (!username.isValid || !email.isValid) {
      return;
    }

    goNext();
  };

  const disableContinue = () => {
    if (
      !data.fullName?.trim() ||
      !!fullNameError ||
      !username.isValid ||
      !email.isValid ||
      username.isChecking ||
      email.isChecking
    ) {
      return true;
    }
    return false;
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300 mx-auto max-w-[270px] sm:max-w-[325px]">
      <div className="space-y-6">
        <div className="space-y-2 relative">
          <Label htmlFor="full-name">Full Name*</Label>
          <Input
            id="full-name"
            placeholder="John Doe"
            value={data.fullName || ""}
            required
            onBlur={handleFullNameBlur}
            onChange={(e) => {
              updateData({ fullName: e.target.value });
              if (fullNameError) setFullNameError(null);
            }}
            aria-invalid={!!fullNameError}
          />
          <div className="absolute top-full right-0 pt-1">
            {fullNameError && (
              <p className="text-xs text-destructive text-right">
                {fullNameError}
              </p>
            )}
          </div>
        </div>

        <div className="space-y-2 relative">
          <Label htmlFor="username">Username*</Label>
          <Input
            id="username"
            placeholder="johndoe"
            required
            value={username.value}
            onChange={(e) => username.setValue(e.target.value)}
            aria-invalid={!!username.error}
          />
          <div className="absolute top-full right-0">
            {username.isChecking && (
              <p className="text-xs text-muted-foreground text-right">
                Checking availability...
              </p>
            )}
            {username.error && (
              <p className="text-xs text-destructive text-right">
                {username.error}
              </p>
            )}
            {username.isValid && !username.isChecking && (
              <p className="text-xs text-green-500 text-right">
                Username is available
              </p>
            )}
          </div>
        </div>

        <div className="space-y-2 relative">
          <Label htmlFor="email">Email*</Label>
          <Input
            id="email"
            type="email"
            placeholder="m@example.com"
            value={email.value}
            required
            onChange={(e) => email.setValue(e.target.value)}
            aria-invalid={!!email.error}
          />
          <div className="absolute top-full right-0">
            {email.isChecking && (
              <p className="text-xs text-muted-foreground text-right">
                Checking availability...
              </p>
            )}
            {email.error && (
              <p className="text-xs text-destructive text-right">
                {email.error}
              </p>
            )}
            {email.isValid && !email.isChecking && (
              <p className="text-xs text-green-500 text-right">
                Email is available
              </p>
            )}
          </div>
        </div>
      </div>
      <div className="flex justify-end gap-4 pt-6">
        <Button variant="outline" onClick={goBack} className="">
          Back
        </Button>
        <Button
          disabled={disableContinue()}
          className=""
          onClick={handleContinue}
        >
          Continue
        </Button>
      </div>
    </div>
  );
}
