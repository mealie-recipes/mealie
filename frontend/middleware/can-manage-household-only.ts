interface CanManageRedirectParams {
  $auth: any
  redirect: (path: string) => void
}
export default function ({ $auth, redirect }: CanManageRedirectParams) {
  // If the user is not allowed to manage group settings redirect to the home page
  if (!$auth.user?.canManageHousehold) {
    console.warn("User is not allowed to manage household settings");
    return redirect("/");
  }
}
