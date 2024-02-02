interface GroupOnlyRedirectParams {
  $auth: any
  route: any
  redirect: (path: string) => void
}

export default function ({ $auth, route, redirect }: GroupOnlyRedirectParams) {
  // this can only be used for routes that have a groupSlug parameter (e.g. /g/:groupSlug/...)
  if (route.params.groupSlug !== $auth.user.groupSlug) {
    redirect("/")
  }
}
