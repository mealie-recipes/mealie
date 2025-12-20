"use client";
import { useAuth } from "@/lib/auth/auth-context";
import { Button } from "./button";

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
