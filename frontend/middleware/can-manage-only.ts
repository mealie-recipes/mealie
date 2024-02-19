interface CanManageRedirectParams {
  $auth: any
  redirect: (path: string) => void
}
export default function ({ $auth, redirect }: CanManageRedirectParams) {
  // If the user is not allowed to manage group settings redirect to the home page
  console.log($auth.user)
  if (!$auth.user.canManage) {
    console.warn("User is not allowed to manage group settings");
    return redirect("/")
  }
}
