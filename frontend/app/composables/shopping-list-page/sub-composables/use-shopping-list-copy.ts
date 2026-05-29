import type { ShoppingListItemOut } from "~/lib/api/types/household";
import { useCopy, useCopyList } from "~/composables/use-copy";

type CopyTypes = "plain" | "markdown";
const notesCheckbox = "\u2610";

/**
 * Composable for managing shopping list copy functionality
 */
export function useShoppingListCopy() {
  const copy = useCopyList();
  const { copyText } = useCopy();

  function copyListItems(itemsByLabel: { [key: string]: ShoppingListItemOut[] }, copyType: CopyTypes) {
    const text: string[] = [];
    Object.entries(itemsByLabel).forEach(([label, items], idx) => {
      if (idx) {
        text.push("");
      }

      text.push(formatCopiedLabelHeading(copyType, label));
      items.forEach(item => text.push(formatCopiedListItem(copyType, item)));
    });

    copy.copyPlain(text);
  }

  async function shareListItemsToNotes(itemsByLabel: { [key: string]: ShoppingListItemOut[] }, title: string) {
    const text = formatAppleNotesShareText(itemsByLabel, title);
    const htmlFile = createAppleNotesHtmlFile(itemsByLabel, title);
    const fileShareData = { title, files: [htmlFile] };

    if (typeof navigator !== "undefined" && navigator.share && navigator.canShare?.(fileShareData)) {
      try {
        await navigator.share(fileShareData);
        return;
      }
      catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
      }
    }

    if (typeof navigator !== "undefined" && navigator.share) {
      try {
        await navigator.share({ title, text });
        return;
      }
      catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
      }
    }

    copyText(text);
  }

  function formatAppleNotesShareText(itemsByLabel: { [key: string]: ShoppingListItemOut[] }, title: string) {
    const text: string[] = [title];

    Object.entries(itemsByLabel).forEach(([label, items]) => {
      if (!items.length) {
        return;
      }

      text.push("", label);
      items.forEach(item => text.push(`${notesCheckbox} ${item.display || ""}`));
    });

    return text.join("\n");
  }

  function createAppleNotesHtmlFile(itemsByLabel: { [key: string]: ShoppingListItemOut[] }, title: string) {
    const html = formatAppleNotesShareHtml(itemsByLabel, title);
    const filename = `${safeFilename(title || "shopping-list")}.html`;

    return new File([html], filename, { type: "text/html" });
  }

  function formatAppleNotesShareHtml(itemsByLabel: { [key: string]: ShoppingListItemOut[] }, title: string) {
    const sections = Object.entries(itemsByLabel)
      .filter(([, items]) => items.length > 0)
      .map(([label, items]) => `
        <section>
          <h2>${escapeHtml(label)}</h2>
          <ul>
            ${items.map(item => `
              <li>
                <span class="checkbox"></span>
                <span>${escapeHtml(item.display || "")}</span>
              </li>
            `).join("")}
          </ul>
        </section>
      `)
      .join("");

    return `<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>${escapeHtml(title)}</title>
    <style>
      body {
        font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
        font-size: 17px;
        line-height: 1.35;
      }
      h1 {
        font-size: 22px;
        margin: 0 0 18px;
      }
      h2 {
        font-size: 18px;
        margin: 18px 0 8px;
      }
      ul {
        list-style: none;
        margin: 0;
        padding: 0;
      }
      li {
        align-items: flex-start;
        display: flex;
        gap: 8px;
        margin: 6px 0;
      }
      .checkbox {
        border: 1.5px solid currentColor;
        border-radius: 50%;
        box-sizing: border-box;
        flex: 0 0 auto;
        height: 18px;
        margin-top: 2px;
        width: 18px;
      }
    </style>
  </head>
  <body>
    <h1>${escapeHtml(title)}</h1>
    ${sections}
  </body>
</html>`;
  }

  function escapeHtml(value: string) {
    return value
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function safeFilename(value: string) {
    return value
      .trim()
      .replace(/[^a-z0-9]+/gi, "-")
      .replace(/^-+|-+$/g, "")
      .toLowerCase() || "shopping-list";
  }

  function formatCopiedListItem(copyType: CopyTypes, item: ShoppingListItemOut): string {
    const display = item.display || "";
    switch (copyType) {
      case "markdown":
        return `- [ ] ${display}`;
      default:
        return display;
    }
  }

  function formatCopiedLabelHeading(copyType: CopyTypes, label: string): string {
    switch (copyType) {
      case "markdown":
        return `# ${label}`;
      default:
        return `[${label}]`;
    }
  }

  return {
    copyListItems,
    shareListItemsToNotes,
    formatCopiedListItem,
    formatCopiedLabelHeading,
    formatAppleNotesShareText,
    formatAppleNotesShareHtml,
  };
}
