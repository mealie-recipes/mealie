"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { useRegistration } from "./registration-context";

/**
 * Render a form that collects a group registration token and provides Back/Continue actions.
 *
 * The component displays an input for a group token and two buttons. The Back button triggers
 * the registration context's `goBack`. The Continue button is disabled when the token is empty
 * after trimming; when clicked it trims the token, calls `updateData({ token })` on the
 * registration context, and then calls `goNext`.
 *
 * @returns A JSX element containing the token input and action buttons.
 */
export function JoinGroup() {
  const { goBack, goNext, updateData } = useRegistration();
  const [token, setToken] = useState("");

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300 mx-auto max-w-[270px] sm:max-w-[325px]">
      <p className="text-sm text-muted-foreground">
        Please provide the registration token associated with the group that
        you'd like to join. You'll need to obtain this from an existing group
        member.
      </p>
      <div className="space-y-2">
        <Label htmlFor="token">Group Token</Label>
        <Input
          id="token"
          placeholder="Enter token"
          value={token}
          onChange={(e) => setToken(e.target.value)}
        />
      </div>
      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={goBack} className="">
          Back
        </Button>
        <Button
          className=""
          disabled={!token.trim()}
          onClick={() => {
            const trimmed = token.trim();
            updateData({ token: trimmed });
            goNext();
          }}
        >
          Continue
        </Button>
      </div>
    </div>
  );
}
