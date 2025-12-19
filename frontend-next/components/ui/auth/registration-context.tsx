"use client";

import { validateAvailability } from "@/lib/api/public/validators";
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
  goNext: () => void;
}

const RegistrationContext = createContext<RegistrationContextType | undefined>(
  undefined
);

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
    setIsValid(false);
    lastCheckedValue.current = trimmed;

    try {
      const available = await validateAvailability(type, trimmed);
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
      if (value) {
        validate();
      }
    }, 800);

    return () => clearTimeout(timer);
  }, [value, validate]);

  const handleChange = (newValue: string) => {
    const trimmed = newValue.trim();
    setValue(trimmed);
    if (onUpdate) onUpdate(trimmed);
    // Reset validity when changing if it doesn't match the last checked value
    if (trimmed !== lastCheckedValue.current) {
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

export function RegistrationProvider({ children }: { children: ReactNode }) {
  const [step, setStep] = useState<RegistrationStep>(1);
  const [groupMode, setGroupMode] = useState<GroupMode>("selection");
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

  const goNext = () => {
    if (step === 1) {
      if (groupMode === "join" && !data.token) return;
      if (
        groupMode === "create" &&
        (!groupNameVal.isValid || groupNameVal.isChecking)
      )
        return;
      setStep(2);
    } else if (step === 2) {
      if (!usernameVal.isValid || usernameVal.isChecking) return;
      if (!data.fullName?.trim()) return;
      setStep(3);
    } else if (step === 3) {
      if (!emailVal.isValid || emailVal.isChecking) return;
      if (!data.password || data.password !== data.confirmPassword) return;
      setStep(4);
    } else if (step === 4) {
      setStep(5);
    } else if (step === 5) {
      console.log("Final Submission Data:", data);
      // Trigger loading state during account creation (debugging placeholder)
      setCreatingAccount(true);
      try {
        // TODO: Call API
        // await createAccount(data);
        // On success: redirect or show success screen
      } catch (error) {
        console.error("Account creation failed:", error);
        // Show error to user
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

export function useRegistration() {
  const context = useContext(RegistrationContext);
  if (context === undefined) {
    throw new Error(
      "useRegistration must be used within a RegistrationProvider"
    );
  }
  return context;
}
