import type { UserOut } from "~/lib/api/types/user";

declare module "#auth-utils" {
  type User = UserOut;

  type UserSession = object;

  type SecureSessionData = object;
}

export { };
