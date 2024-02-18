interface CanOrganizeRedirectParams {
    $auth: any
    redirect: (path: string) => void
}
export default function ({ $auth, redirect }: CanOrganizeRedirectParams) {
    // If the user is not allowed to organize redirect to the home page
    if (!$auth.user.canOrganize) {
        console.warn("User is not allowed to organize data");
        return redirect("/")
    }
}
