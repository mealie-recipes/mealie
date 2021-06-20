/* Add target="_blank" to external links */
/* Source: https://html.com/attributes/a-target/#:~:text=browser */
function externalLinks() {
  for (var c = document.getElementsByTagName("a"), a = 0; a < c.length; a++) {
    var b = c[a];
    b.getAttribute("href") &&
      b.hostname !== location.hostname &&
      (b.target = "_blank");
  }
}
externalLinks();
