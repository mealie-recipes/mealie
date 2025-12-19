export interface CreateUserRegistration {
  group?: string | null;
  household?: string | null;
  groupToken?: string | null;
  email: string;
  username: string;
  fullName: string;
  password: string;
  passwordConfirm: string;
  advanced?: boolean;
  private?: boolean;
  seedData?: boolean;
  locale?: string;
}
export interface CredentialsRequest {
  username: string;
  password: string;
  remember_me?: boolean;
}
export interface DeleteTokenResponse {
  tokenDelete: string;
}
export interface ForgotPassword {
  email: string;
}
