"use client";

import { authApi } from "@/lib/api/auth";
import { validatorsApi } from "@/lib/api/public/validators";
import { useRouter } from "next/navigation";
import {
  createContext,
  useContext,
  useState,
  ReactNode,
  useEffect,
  useRef,
  useCallback,
} from "react";

export type GroupMode = "selection" | "join" | "create";
export type RegistrationStep = 1 | 2 | 3 | 4 | 5;

export interface RegistrationData {
  username?: string;
  fullName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  advancedContent?: boolean;

  groupName?: string;
  privateRecipes?: boolean;
  seedData?: boolean;
  token?: string;
}

export interface ValidationState {
  value: string;
  setValue: (value: string) => void;
  error: string | null;
  isValid: boolean;
  isChecking: boolean;
  validate: () => Promise<void>;
}

interface RegistrationContextType {
  // State
  step: RegistrationStep;
  groupMode: GroupMode;
  data: RegistrationData;
  creatingAccount: boolean;
  submitError: string | null;

  // Validations
  validations: {
    username: ValidationState;
    email: ValidationState;
    groupName: ValidationState;
  };

  // Actions
  setGroupMode: (mode: GroupMode) => void;
  updateData: (data: Partial<RegistrationData>) => void;

  // Navigation
  goBack: () => void;
  goNext: () => Promise<void>;
}

const RegistrationContext = createContext<RegistrationContextType | undefined>(
  undefined
);

/**
 * Provides debounced, async availability validation for a single input field.
 *
 * Validates the current value (after an 800ms debounce) against a remote availability check and exposes state for value, error, validity, and in-progress checking. Triggers a basic email format check when `type` is "email".
 *
 * @param type - The kind of value to validate: `"group"`, `"user"`, or `"email"`.
 * @param initialValue - Initial input value.
 * @param onUpdate - Optional callback invoked whenever the input value changes.
 * @returns An object with:
 *  - `value` — the current input string.
 *  - `setValue` — function to update the input (calls `onUpdate` if provided).
 *  - `error` — a user-facing error message or `null` when there is no error.
 *  - `isValid` — `true` when the last validated value is available; `false` otherwise.
 *  - `isChecking` — `true` while an async validation is in progress.
 *  - `validate` — function that performs an immediate validation and resolves when finished.
 */
function useDebouncedValidation(
  type: "group" | "user" | "email",
  initialValue: string = "",
  onUpdate?: (value: string) => void
) {
  const [value, setValue] = useState(initialValue);
  const [error, setError] = useState<string | null>(null);
  const [isValid, setIsValid] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const lastCheckedValue = useRef<string | null>(null);

  const validate = useCallback(async () => {
    // Only trim here for validation, not in state
    const trimmed = value.trim();

    if (!trimmed) {
      setError(null);
      setIsValid(false);
      return;
    }

    // Email specific regex validation
    if (type === "email") {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(trimmed)) {
        setError("Please enter a valid email address");
        setIsValid(false);
        return;
      }
    }

    if (trimmed === lastCheckedValue.current) {
      return;
    }

    setIsChecking(true);
    setIsValid(false); // Assume false while checking
    lastCheckedValue.current = trimmed;

    try {
      const available = await validatorsApi.validateAvailability(type, trimmed);

      // Ignore stale responses if the current value changed since request
      if (lastCheckedValue.current !== trimmed) {
        return;
      }

      if (!available) {
        setError(
          type === "group"
            ? "Group name is already taken"
            : type === "email"
            ? "Email is already in use"
            : "Username is already taken"
        );
        setIsValid(false);
      } else {
        setError(null);
        setIsValid(true);
      }
    } catch (error) {
      console.error(`Failed to validate ${type}`, error);
      setError("Unable to validate right now. Please try again.");
      setIsValid(false);
      lastCheckedValue.current = null;
    } finally {
      setIsChecking(false);
    }
  }, [value, type]);

  useEffect(() => {
    const timer = setTimeout(() => {
      // Don't validate empty strings automatically
      if (value) {
        validate();
      }
    }, 800);

    return () => clearTimeout(timer);
  }, [value, validate]);

  const handleChange = (newValue: string) => {
    setValue(newValue);
    if (onUpdate) onUpdate(newValue);
    if (newValue.trim() !== lastCheckedValue.current) {
      setIsValid(false);
    }
  };

  return {
    value,
    setValue: handleChange,
    error,
    isValid,
    isChecking,
    validate,
  };
}

/**
 * Provides registration state, debounced field validations, and navigation/actions for the multi-step registration flow to descendant components.
 *
 * @param children - Child elements that will receive the registration context
 * @returns A React context provider element exposing the current registration step, group mode, collected data, validation states, submission status, and action handlers (setGroupMode, updateData, goBack, goNext)
 */
export function RegistrationProvider({ children }: { children: ReactNode }) {
  const [step, setStep] = useState<RegistrationStep>(1);
  const [groupMode, setGroupMode] = useState<GroupMode>("selection");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const router = useRouter();

  const [data, setData] = useState<RegistrationData>({
    username: "",
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    advancedContent: false,
  });
  const [creatingAccount, setCreatingAccount] = useState<boolean>(false);

  const updateData = (newData: Partial<RegistrationData>) => {
    setData((prev) => ({ ...prev, ...newData }));
    if (submitError) setSubmitError(null);
  };

  // Validations
  const usernameVal = useDebouncedValidation("user", data.username || "", (v) =>
    updateData({ username: v })
  );
  const emailVal = useDebouncedValidation("email", data.email || "", (v) =>
    updateData({ email: v })
  );
  const groupNameVal = useDebouncedValidation(
    "group",
    data.groupName || "",
    (v) => updateData({ groupName: v })
  );

  const goNext = async () => {
    setSubmitError(null);

    if (step === 1) {
      if (groupMode === "join" && !data.token) return;
      if (
        groupMode === "create" &&
        (!groupNameVal.isValid || groupNameVal.isChecking)
      ) {
        groupNameVal.validate();
        return;
      }
      setStep(2);
    } else if (step === 2) {
      if (!usernameVal.isValid || usernameVal.isChecking) {
        usernameVal.validate();
        return;
      }
      if (!data.fullName?.trim()) return;
      setStep(3);
    } else if (step === 3) {
      if (!emailVal.isValid || emailVal.isChecking) {
        emailVal.validate();
        return;
      }
      if (!data.password || data.password !== data.confirmPassword) return;
      setStep(4);
    } else if (step === 4) {
      setStep(5);
    } else if (step === 5) {
      setCreatingAccount(true);
      try {
        const user = {
          username: data.username!,
          fullName: data.fullName!,
          email: data.email!,
          password: data.password!,
          passwordConfirm: data.confirmPassword!,
          group: groupMode === "create" ? data.groupName : undefined,
          groupToken: groupMode === "join" ? data.token : undefined,
          advanced: data.advancedContent || false,
          private: data.privateRecipes || false,
          seedData: data.seedData || false,
        };

        await authApi.registerUser(user);
        await authApi.fetchToken({
          username: data.username!,
          password: data.password!,
          remember_me: true,
        });

        router.push("/");
      } catch (error: any) {
        console.error("Account creation failed:", error);
        setSubmitError(
          error.message || "Failed to create account. Please try again."
        );
      } finally {
        setCreatingAccount(false);
      }
    }
  };

  const goBack = () => {
    if (step === 5) setStep(4);
    else if (step === 4) setStep(3);
    else if (step === 3) setStep(2);
    else if (step === 2) setStep(1);
    else if (step === 1) {
      if (groupMode !== "selection") setGroupMode("selection");
    }
  };

  return (
    <RegistrationContext.Provider
      value={{
        step,
        groupMode,
        data,
        creatingAccount,
        submitError,
        validations: {
          username: usernameVal,
          email: emailVal,
          groupName: groupNameVal,
        },
        setGroupMode,
        updateData,
        goBack,
        goNext,
      }}
    >
      {children}
    </RegistrationContext.Provider>
  );
}

/**
 * Accesses the registration context for the current component tree.
 *
 * @returns The registration context value provided by `RegistrationProvider`.
 * @throws If called outside of a `RegistrationProvider`, throws an `Error` stating it must be used within a `RegistrationProvider`.
 */
export function useRegistration() {
  const context = useContext(RegistrationContext);
  if (context === undefined) {
    throw new Error(
      "useRegistration must be used within a RegistrationProvider"
    );
  }
  return context;
}