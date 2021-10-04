import { BaseAPI } from "./_base";

const routes = {
  base: "/api/admin/email",
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

export class EmailAPI extends BaseAPI {
  check() {
    return this.requests.get<CheckEmailResponse>(routes.base);
  }

  test(payload: TestEmailPayload) {
    return this.requests.post<TestEmailResponse>(routes.base, payload);
  }
}
