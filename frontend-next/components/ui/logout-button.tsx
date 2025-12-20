"use client";
import { useAuth } from "@/lib/auth/auth-context";
import { Button } from "./button";

/**
 * Renders a logout button that signs the current user out when clicked.
 *
 * Uses the authentication context to call the sign-out handler.
 *
 * @returns A React element: a Button that triggers the authentication sign-out when activated.
 */
export function LogoutButton() {
  const { signOut } = useAuth();

  const handleLogout = async () => {
    await signOut();
  };

  return (
    <Button onClick={handleLogout} variant="default">
      Logout
    </Button>
  );
}