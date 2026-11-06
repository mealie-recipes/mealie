!!! info
    This guide was submitted by a community member. Find something wrong? Submit a PR to get it fixed!

[Mealie Share](https://apps.apple.com/us/app/mealie-share/id6802041367) is a free, open-source iOS app that adds a Share Extension to your iPhone or iPad. It lets you save a recipe to your Mealie instance from the iOS Share Sheet, from Safari, Instagram, or any other app that can share a link.

The source code is available on [GitHub](https://github.com/lmieulet/mealie-share-ios) under the MPL-2.0 license.

## Requirements

- iOS 16.0 or later
- A Mealie instance reachable from your device
- A Mealie API token

## Initial Setup

1. Install [Mealie Share from the App Store](https://apps.apple.com/us/app/mealie-share/id6802041367).
2. Create an API token in Mealie: navigate to `http://YOUR_MEALIE_URL/user/profile/api-tokens`, or click your profile picture in the top left -> API Tokens.
3. Open the Mealie Share app and enter the full URL of your Mealie instance (e.g. `http://10.0.0.5:9000` or `https://mealie.domain.com`) and the API token.
4. Use the **Test Connection** button to check the settings, then save them.

!!! warning
    An API token gives the same access as your user account. Treat it like a password.

The URL and token are stored in the iOS Keychain and shared with the extension. The app does not include ads, tracking, or analytics, and only communicates with the Mealie server you configure.

## Using the Share Extension

1. In Safari (or any other app), open the recipe page and tap the **Share** button.
2. Select **Mealie Share** in the share sheet. If it is not listed, scroll to the end of the row, tap **More**, and enable it.
3. The link is sent to Mealie's recipe import from URL feature, and the result is displayed once the import finishes.

!!! note
    The extension relies on Mealie's recipe scraper. Some websites block scrapers or require JavaScript, in which case the import fails and the error returned by Mealie is shown. For those sites, see the [iOS Shortcut](./ios-shortcut.md) guide, which can send the page's HTML captured in Safari.
