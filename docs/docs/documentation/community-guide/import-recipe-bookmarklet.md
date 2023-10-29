<!-- prettier-ignore -->
!!! info
    This guide was submitted by a community member. Find something wrong? Submit a PR to get it fixed!

You can use bookmarklets to generate a bookmark that will take your current location, and open a new tab that will try to import that URL into Mealie.

You can use a [bookmarklet generator site](https://caiorss.github.io/bookmarklet-maker/) and the code below to generate a bookmark for your site. Just change the `http://localhost:8080` to your sites web address and follow the instructions.

<!-- prettier-ignore -->
!!! note
    There is no trailing `/` at the end of the url!

```js
var url = document.URL;
var mealie = "http://localhost:8080";
var use_keywords= "&use_keywords=1" // Optional - use keywords from recipe - update to "" if you don't want that
var edity = "&edit=1" // Optional - keep in edit mode - update to "" if you don't want that
var dest = mealie + "/r/create/url?recipe_import_url=" + url + use_keywords + edity;
window.open(dest, "_blank");
```
