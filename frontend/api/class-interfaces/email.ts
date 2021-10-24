import { BaseAPI } from "../_base";

const routes = {
  base: "/api/admin/email",
  forgotPassword: "/api/users/forgot-password",

  invitation: "/api/groups/invitations/email",
};

export interface EmailResponse {
  success: boolean;
  error: string;
}

export interface EmailPayload {
  email: string;
}

export interface InvitationEmail {
  email: string;
  token: string;
}

export class EmailAPI extends BaseAPI {
  test(payload: EmailPayload) {
    return this.requests.post<EmailResponse>(routes.base, payload);
  }

  sendInvitation(payload: InvitationEmail) {
    return this.requests.post<EmailResponse>(routes.invitation, payload);
  }

  sendForgotPassword(payload: EmailPayload) {
    return this.requests.post<EmailResponse>(routes.forgotPassword, payload);
  }
}
