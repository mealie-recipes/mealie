interface AdvancedOnlyRedirectParams {
    $auth: any
    redirect: (path: string) => void
}
export default function ({ $auth, redirect }: AdvancedOnlyRedirectParams) {
    // If the user is not allowed to access advanced features redirect to the home page
    if (!$auth.user.advanced) {
        console.warn("User is not allowed to access advanced features");
        return redirect("/")
    }
}
