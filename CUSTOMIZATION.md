# Custom Mealie fork

This fork keeps the Recipe Press integration as a small patch on top of
`mealie-recipes/mealie:mealie-next`.

## Automated release flow

Every push to `mealie-next` builds a multi-architecture image and publishes it
to `ghcr.io/charlesday/mealie` with an immutable `sha-<commit>` tag. The
workflow then sends the tag and registry digest to Home Utility. Home Utility
validates those values and opens or updates a deployment PR. Merging that PR
runs the existing homelab deployment.

Configure these repository settings before merging the customization PR:

- Actions secret `MEALIE_AUTOMATION_TOKEN`: a fine-grained personal access
  token with access to both `CharlesDay/mealie` and `CharlesDay/home-utility`,
  with repository permissions `Contents: Read and write` and
  `Pull requests: Read and write`.
- Optional Actions variable `RECIPE_PRESS_URL`: the browser-visible Recipe
  Press address. It defaults to
  `http://paprika-recipe-generator.home.arpa`.

The same `MEALIE_AUTOMATION_TOKEN` must be stored as an Actions secret in Home
Utility. The custom GHCR package may be made public so the cluster can pull it
without an additional registry credential.

## Upstream updates

The scheduled upstream-sync workflow runs daily and merges the official
`mealie-next` branch into `automation/upstream-sync`. It opens a PR whenever
new upstream commits exist. Merge conflicts intentionally fail the workflow so
custom changes are never silently discarded.
