import { BaseAPI } from "./_base";

const routes = {
  base: "/api/admin/email",

  invitation: "/api/groups/invitations/email",
};

export interface CheckEmailResponse {
  ready: boolean;
}

export interface TestEmailResponse {
  success: boolean;
  error: string;
}

export interface TestEmailPayload {
  email: string;
}

export interface InvitationEmail {
  email: string;
  token: string;
}

export interface InvitationEmailResponse {
  success: boolean;
  error: string;
}

export class EmailAPI extends BaseAPI {
  check() {
    return this.requests.get<CheckEmailResponse>(routes.base);
  }

  test(payload: TestEmailPayload) {
    return this.requests.post<TestEmailResponse>(routes.base, payload);
  }

  sendInvitation(payload: InvitationEmail) {
    return this.requests.post<InvitationEmailResponse>(routes.invitation, payload);
  }
}
