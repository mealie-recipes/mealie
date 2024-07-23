import { BaseAPI } from "../base/base-clients";
import { EmailInitationResponse, EmailInvitation } from "~/lib/api/types/household";
import { ForgotPassword } from "~/lib/api/types/user";
import { EmailTest } from "~/lib/api/types/admin";

const routes = {
  base: "/api/admin/email",
  forgotPassword: "/api/users/forgot-password",

  invitation: "/api/households/invitations/email",
};

export class EmailAPI extends BaseAPI {
  test(payload: EmailTest) {
    return this.requests.post<EmailInitationResponse>(routes.base, payload);
  }

  sendInvitation(payload: EmailInvitation) {
    return this.requests.post<EmailInitationResponse>(routes.invitation, payload);
  }

  sendForgotPassword(payload: ForgotPassword) {
    return this.requests.post<EmailInitationResponse>(routes.forgotPassword, payload);
  }
}
