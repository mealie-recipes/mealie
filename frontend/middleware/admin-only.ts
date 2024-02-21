interface AdminRedirectParams {
    $auth: any
    redirect: (path: string) => void
}
export default function ({ $auth, redirect }: AdminRedirectParams) {
    // If the user is not an admin redirect to the home page
    if (!$auth.user.admin) {
        return redirect("/")
    }
}
