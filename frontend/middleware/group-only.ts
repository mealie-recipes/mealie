interface GroupOnlyRedirectParams {
  $auth: any
  route: any
  redirect: (path: string) => void
}

export default function ({ $auth, route, redirect }: GroupOnlyRedirectParams) {
  if (route.params.groupSlug !== $auth.user.groupSlug) {
    redirect("/")
  }
}
