import { scorePassword } from "@/lib/auth/password";
import { Check, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "../card";

interface PasswordStrengthProps {
  password: string;
}

/**
 * Map a password to a human-readable strength label, a Tailwind text color class, and a numeric strength score.
 *
 * @returns An object with:
 *  - `label` — one of `"Very Strong"`, `"Strong"`, `"Good"`, `"Fair"`, or `"Weak"`;
 *  - `color` — a Tailwind CSS text color class corresponding to the label;
 *  - `score` — a numeric strength score (0–100) for the provided password
 */
export function getPasswordStrength(password: string) {
  const score = scorePassword(password);
  if (score > 90)
    return { label: "Very Strong", color: "text-emerald-600", score };
  if (score > 70) return { label: "Strong", color: "text-green-500", score };
  if (score > 50) return { label: "Good", color: "text-yellow-500", score };
  if (score > 30) return { label: "Fair", color: "text-orange-500", score };
  return { label: "Weak", color: "text-red-500", score };
}

/**
 * Render a password strength UI showing a colored progress bar, a strength label, a checklist of criteria, and an optional flagged-word warning.
 *
 * @param password - The password string to evaluate and display strength information for.
 * @returns A JSX element containing the strength bar, labeled strength, criteria checks, and a warning if the password includes common weak words.
 */
export function PasswordStrength({ password }: PasswordStrengthProps) {
  const { label, color: textColor, score } = getPasswordStrength(password);

  const criteria = [
    { label: "At least 8 characters", met: password.length >= 8 },
    { label: "Contains lowercase", met: /[a-z]/.test(password) },
    { label: "Contains uppercase", met: /[A-Z]/.test(password) },
    { label: "Contains number", met: /\d/.test(password) },
    { label: "Contains special character", met: /\W/.test(password) },
  ];

  const flaggedWords = ["password", "mealie", "admin", "qwerty", "login"];
  const hasFlaggedWord = flaggedWords.some((word) =>
    password.toLowerCase().includes(word)
  );

  let barColor = "bg-red-500";

  if (score > 90) {
    barColor = "bg-emerald-600";
  } else if (score > 70) {
    barColor = "bg-green-500";
  } else if (score > 50) {
    barColor = "bg-yellow-500";
  } else if (score > 30) {
    barColor = "bg-orange-500";
  } else {
    barColor = "bg-red-500";
  }

  return (
    <Card className="bg-secondary/50">
      <CardContent className="space-y-3">
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Password Strength</span>
            <span className={cn("font-medium", textColor)}>{label}</span>
          </div>
          <div className="h-1.5 w-full bg-input/20 dark:bg-input/30 rounded-full overflow-hidden">
            <div
              className={cn("h-full transition-all duration-300", barColor)}
              style={{ width: `${score}%` }}
            />
          </div>
        </div>

        <ul className="text-xs space-y-1">
          {criteria.map((item, index) => (
            <li
              key={index}
              className={cn(
                "flex items-center gap-2",
                item.met ? "text-green-500" : "text-muted-foreground"
              )}
            >
              {item.met ? (
                <Check className="w-3 h-3" />
              ) : (
                <div className="w-3 h-3 rounded-full border border-current opacity-50" />
              )}
              {item.label}
            </li>
          ))}
          {hasFlaggedWord && (
            <li className="flex items-center gap-2 text-red-500 dark:text-red-400">
              <X className="w-3 h-3" />
              Avoid common words (password, admin, etc.)
            </li>
          )}
        </ul>
      </CardContent>
    </Card>
  );
}
