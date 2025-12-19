"use client";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Check, X } from "lucide-react";
import { useRegistration } from "./registration-context";
import { getPasswordStrength } from "./password-strength";

/**
 * Renders a review step that displays submitted account and group information for final confirmation.
 *
 * Shows group-specific fields when `groupMode` is "create" (Group Name, Seed Data, Keep Private) or "join" (Group Token),
 * always shows Full Name, Username, Email, Password (with strength label), and Advanced Content,
 * and provides Back and Create buttons wired to the registration flow's `goBack` and `goNext` handlers.
 *
 * @returns A React element containing the review UI for confirming account creation or joining a group.
 */
export function AccountReview() {
  const { data, groupMode, goBack, goNext } = useRegistration();

  const ReviewItem = ({
    label,
    value,
  }: {
    label: string;
    value: React.ReactNode;
  }) => (
    <div className="flex justify-between items-center py-2 border-b last:border-0 gap-4">
    <span className="text-sm font-medium text-muted-foreground whitespace-nowrap">
      {label}
    </span>
      <span className="text-sm font-semibold text-right truncate">{value}</span>
    </div>
  );

  const BooleanValue = ({ value }: { value?: boolean }) => {
    return value ? (
      <span className="flex items-center text-green-600 gap-1">
        <Check className="h-4 w-4" /> Yes
      </span>
    ) : (
      <span className="flex items-center text-muted-foreground text-destructive gap-1">
        <X className="h-4 w-4" /> No
      </span>
    );
  };

  const PasswordValue = ({ value }: { value?: string }) => {
    const { label, color } = getPasswordStrength(value || "");
    return <span className={color}>{label}</span>;
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300 mx-auto max-w-[270px] sm:max-w-[325px]">
      <div className="space-y-1">
        <h3 className="font-semibold text-lg">Review Details</h3>
        <p className="text-sm text-muted-foreground">
          Please review your information before creating your account.
        </p>
      </div>

      <div className="rounded-lg border p-4 space-y-1">
        {groupMode === "create" && (
          <>
            <ReviewItem label="Group Name" value={data.groupName} />
            <ReviewItem
              label="Seed Data"
              value={<BooleanValue value={data.seedData} />}
            />
            <ReviewItem
              label="Keep Private"
              value={<BooleanValue value={data.privateRecipes} />}
            />
          </>
        )}
        {groupMode === "join" && (
          <ReviewItem label="Group Token" value={data.token} />
        )}

        <ReviewItem label="Full Name" value={data.fullName} />
        <ReviewItem label="Username" value={data.username} />
        <ReviewItem label="Email" value={data.email} />
        <ReviewItem
          label="Password"
          value={<PasswordValue value={data.password} />}
        />
        <ReviewItem
          label="Advanced Content"
          value={<BooleanValue value={data.advancedContent} />}
        />
      </div>

      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={goBack} className="">
          Back
        </Button>
        <Button className="" onClick={goNext}>
          Create
        </Button>
      </div>
    </div>
  );
}
