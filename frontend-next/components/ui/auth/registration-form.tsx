"use client";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Users, Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import { AppConfig } from "@/lib/types/app";
import BasicError from "../custom/basic-error";
import { ActionCard, ActionCardGroup } from "../custom/auth/action-cards";
import { JoinGroup } from "./join-group";
import { CreateGroup } from "./create-group";
import { AccountDetails } from "./account-details";
import { AccountSecurity } from "./account-security";
import { AccountPreferences } from "./account-preferences";
import { AccountReview } from "./account-review";
import { RegistrationProvider, useRegistration } from "./registration-context";
import Loader from "../custom/loader";

interface RegistrationFormProps extends React.ComponentProps<"div"> {
  config: AppConfig;
}

export function RegistrationForm({
  className,
  config,
  ...props
}: RegistrationFormProps) {
  // Gate registration by signup availability instead of login methods
  if (!config.allowSignup) {
    return (
      <BasicError error="Registration is disabled. Please contact the administrator." />
    );
  }

  return (
    <RegistrationProvider>
      <RegistrationFormContent className={className} {...props} />
    </RegistrationProvider>
  );
}

function RegistrationFormContent({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const router = useRouter();
  const { step, groupMode, setGroupMode, goNext, updateData, creatingAccount } =
    useRegistration();

  const getStepTitle = () => {
    if (step === 1) {
      if (groupMode === "join") return "Join a Group";
      if (groupMode === "create") return "Create Group";
      return "Group Selection";
    }
    if (step === 2) return "User Details";
    if (step === 3) return "Security";
    if (step === 4) return "Preferences";
    if (step === 5) return "Review";
    return "";
  };

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center w-full gap-6",
        className
      )}
      {...props}
    >
      <Card
        className={cn(
          "transition-all duration-300 ease-in-out overflow-hidden",
          step === 1 && groupMode === "selection"
            ? "w-full max-w-2xl"
            : "w-[320px] sm:w-[375px]"
        )}
      >
        <CardHeader className="relative pb-2 text-center">
          <CardTitle className="text-2xl font-bold pt-1">
            User Registration
          </CardTitle>
          <CardDescription>
            {!(step === 1 && groupMode === "selection") && !creatingAccount && (
              <div className="animate-in fade-in slide-in-from-top-2 duration-500">
                <div className="flex gap-2 mt-4 mb-2 max-w-[200px] mx-auto">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <div
                      key={s}
                      className={cn(
                        "h-1 flex-1 rounded-full transition-colors duration-300",
                        s <= step ? "bg-primary" : "bg-muted"
                      )}
                    />
                  ))}
                </div>
                <div className="text-xs font-medium text-muted-foreground mt-1">
                  {getStepTitle()}
                </div>
              </div>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent
          className={cn(
            "transition-all duration-500",
            step === 1 && groupMode === "selection"
              ? "px-8 pt-2 pb-6"
              : "px-6 pb-6 pt-2"
          )}
        >
          {creatingAccount && (
            <div className="py-8">
              <Loader />
            </div>
          )}

          {!creatingAccount && (
            <>
              {step === 1 && groupMode === "selection" && (
                <ActionCardGroup
                  onValueChange={(val) => {
                    if (val === "join" || val === "create") {
                      setGroupMode(val);
                    }
                  }}
                >
                  <ActionCard
                    value="join"
                    icon={<Users size={40} />}
                    title="Join a Group"
                    description="Connect to an existing household using an invite token"
                  />
                  <ActionCard
                    value="create"
                    icon={<Plus size={40} />}
                    title="New Group"
                    description="Start fresh by creating a new household organization"
                  />
                </ActionCardGroup>
              )}
              {step === 1 && groupMode === "join" && <JoinGroup />}

              {step === 1 && groupMode === "create" && <CreateGroup />}

              {step === 2 && <AccountDetails />}
              {step === 3 && <AccountSecurity />}
              {step === 4 && <AccountPreferences />}
              {step === 5 && <AccountReview />}
            </>
          )}
        </CardContent>
      </Card>
      <div className="text-sm text-muted-foreground animate-in fade-in duration-500">
        Already have an account?{" "}
        <Button
          variant="link"
          className="p-0 h-auto font-normal"
          onClick={() => router.push("/login")}
        >
          Sign in
        </Button>
      </div>
    </div>
  );
}
