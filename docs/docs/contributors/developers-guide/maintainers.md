# Maintainers Guide

This is the start of the maintainers guide for Mealie developers. Those who have been invited to the GitHub organization and/or those who wish to play a bigger part in the Mealie developers community may find this helpful.

## Managing Issues

If you are working on issues, it can be helpful to understand the workflow for our repository. When an issue comes in it is tagged with the `bug` and `triage` flags. This is to indicate that they need to be reviewed by a maintainer to determine validity.

After you've reviewed an issue it will generally move into one of two states:

`bug:confirmed`
:   Your were able to verify the issue and we determined we need to fix it


`needs more info`
:   The original post does not contain enough information, and if the reporter does not provide additional information, the issue will be automatically closed.

Once you've reviewed an issue and moved it into another category, you should remove the triage label.

### While going through issues try to keep the following in mind

- It is perfectly okay to ignore an issue if it is low quality
- You should close any issues that ignore the standard report template and request they reopen the issue using the proper template
- You should **not** try to reproduce issues that don't have clear reproduction steps, don't have a version provided, or are generally unclear.
- Issues that are not bugs, should likely be converted to discussions.

## Drafting Releases

### Tags

Mealie is published via GitHub actions to the GitHub container registry with the follow tags:

`ghcr.io/mealie-recipes/mealie:nightly`
: published with every push to `mealie-next` branch - [Actions File](https://github.com/mealie-recipes/mealie/blob/mealie-next/.github/workflows/nightly.yml)

`ghcr.io/mealie-recipes/mealie:latest`
: published when a new GitHub Release is created - [Actions File](https://github.com/mealie-recipes/mealie/blob/mealie-next/.github/workflows/release.yml)

`ghcr.io/mealie-recipes/mealie:{version}`
: published when a new GitHub Release is created - [Actions File](https://github.com/mealie-recipes/mealie/blob/mealie-next/.github/workflows/release.yml)

!!! note
    Both the latest, and {version} tags will be the same image on the release of a new version

### Process

Because we've built all our publishing efforts on GitHub Actions we rely primarily on automations to perform our releases. As such creating a new build of Mealie is as simple as creating a new GitHub release. Here are the general steps we take to create a new release

1. Navigate to the [Github Release Page](https://github.com/mealie-recipes/mealie/releases) and click the 'Draft a new release' button.
2. Choose a tag and increment the version according to the semver specification. i.e, **major** version for breaking changes, **minor** for feature updates, and **patch** for bug fixes.
3. Name the Release, usually just the tag is fine, however if there is a special feature you'd like to highlight this would be a great place to do it.
4. Click the "Generate release notes" button which will pull in all the Git Commits as a changelog. For bug fix only releases this is sufficient, however if there are major features, or good quality of life improvements it's good to provide those prior to listing the full changelog.

!!! tip
    Don't worry about setting the version number in the container or code, it's set during the build process and uses the tag you specified when drafting a new release.

    You can see how this is done in the [Actions File](https://github.com/mealie-recipes/mealie/blob/mealie-next/.github/workflows/partial-builder.yml#L35-L37)

### Tags and Releases

Mealie tries to adhere to a strict [Semver](https://semver.org/) policy. This means that we try to keep our releases as stable as possible, and only introduce breaking changes when absolutely necessary. As such we try to keep our releases as follows:

- **Major** releases are reserved for breaking changes, and are not expected to be frequent. Ideally, we will remain at v1.x.x for the forseeable future.
- **Minor** releases are reserved for new features, and are expected to be frequent.
- **Patch** releases are reserved for bug fixes, and are expected to be frequent.

Any maintainer who has privileges on GitHub to create a new release can create a release at any time they feel it is necessary. However, it is recommended that you reach out in the discord to other maintainers and get at least one other maintainer to approve the release.

An important caveat to this is that we _may_ make breaking changes in a minor release if it is security related. In this case, the releaser should headline the release notes with the notice and impact of the breaking change, however we may not bump the major version depending on user impact.

### Release Notes

When drafting a new release, GitHub will automatically pull in all the commits since the last release. This is a great start. After pulling in all of the commits, you should add sections for

- New Features - Any new features that are being introduced in this release (screenshots are great here)
- Bug Fixes - Significant bug fixes that are being introduced in this release, smaller bug fixes can be left out if they are noted in a commit message
- Breaking Changes - Any breaking changes that are being introduced in this release (should be rare)
