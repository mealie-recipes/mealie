"use client";
import { authApi } from "@/lib/api/auth";
import { useRouter } from "next/navigation";
import { Button } from "./button";

export function LogoutButton() {
  const router = useRouter();

  const handleLogout = async () => {
    await authApi.logout();
    router.push("/login");
  };

  return (
    <Button onClick={handleLogout} variant="default">
      Logout
    </Button>
  );
}
