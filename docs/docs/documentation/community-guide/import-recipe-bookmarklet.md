<!-- prettier-ignore -->
!!! info
    This guide was submitted by a community member. Find something wrong? Submit a PR to get it fixed!

You can use bookmarklets to generate a bookmark that will take your current location, and open a new tab that will try to import that URL into Mealie.

You can use a [bookmarklet generator site](https://caiorss.github.io/bookmarklet-maker/) and the code below to generate a bookmark for your site. Just change the `http://localhost:8080` to your sites web address and follow the instructions.

```js
var url = document.URL.endsWith('/') ?
    document.URL.slice(0, -1) :
    document.URL;
var mealie = "http://localhost:8080";
var group_slug = "home" // Change this to your group slug. You can obtain this from your URL after logging-in to Mealie
var use_keywords = "" // Optional: "1" to import the original keywords as tags, "0" to not. Leave empty to use your last choice
var edit = "" // Optional: "1" to stay in edit mode after importing, "0" to not. Leave empty to use your last choice

if (mealie.slice(-1) === "/") {
    mealie = mealie.slice(0, -1)
}
var dest = mealie + "/g/" + group_slug + "/r/create/url"
    + "?use_keywords=" + use_keywords
    + "&edit=" + edit
    + "&recipe_import_url=" + encodeURIComponent(url);
window.open(dest, "_blank");
```
