"use client";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "../checkbox";
import { useRegistration } from "./registration-context";

/**
 * Render account preferences UI used during registration.
 *
 * Consumes the registration context to read and update the `advancedContent` flag and to navigate between steps.
 *
 * @returns A JSX element with a checkbox labeled "Enable Advanced Content" that updates `advancedContent` in context, a descriptive paragraph, and Back / Review Account buttons wired to the registration navigation handlers.
 */
export function AccountPreferences() {
  const { data, updateData, goBack, goNext } = useRegistration();
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300 mx-auto max-w-[270px] sm:max-w-[325px]">
      <div className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="advanced-content"
              checked={data.advancedContent}
              onCheckedChange={(checked) =>
                updateData({ advancedContent: checked === true })
              }
            />
            <Label htmlFor="advanced-content">Enable Advanced Content</Label>
          </div>
          <p className="text-sm text-muted-foreground">
            Enables advanced features like Recipe Scaling, API keys, Webhooks,
            and Data Management. Don't worry, you can always change this later
          </p>
        </div>
      </div>
      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={goBack} className="">
          Back
        </Button>
        <Button className="" onClick={goNext}>
          Review Account
        </Button>
      </div>
    </div>
  );
}
