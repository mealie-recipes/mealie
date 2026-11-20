import { useEventListener } from "@vueuse/core";
import type { MaybeRefOrGetter } from "vue";
import { alert } from "~/composables/use-toast";
import { useGlobalI18n } from "~/composables/use-global-i18n";

interface UsePasteImageOptions {
  /** Called with the image from the clipboard. */
  onImage: (file: File) => void;
  /** Pastes are ignored while this is false. */
  enabled?: MaybeRefOrGetter<boolean>;
}

function isEditable(target: EventTarget | null) {
  return target instanceof HTMLElement
    && (target.isContentEditable || target.matches("input, textarea, select"));
}

// Browsers report some formats under vendor aliases (e.g. image/x-ms-bmp, image/pjpeg)
const MIME_SUBTYPE_ALIASES: Record<string, string> = { "pjpeg": "jpeg", "ms-bmp": "bmp" };

// Clipboard files can arrive unnamed (or named after the OS), but the recipe image endpoint
// reads the extension from the file name, so always give the file a usable one.
function nameImage(file: File) {
  const nameExtension = file.name.match(/\.([a-z0-9]{2,5})$/i)?.[1];
  const subtype = file.type.split("/")[1]?.split("+")[0].replace(/^x-/, "") ?? "";
  const extension = nameExtension || MIME_SUBTYPE_ALIASES[subtype] || subtype || "png";
  return new File([file], `pasted-image.${extension}`, { type: file.type });
}

/**
 * Reads an image from the clipboard on demand, for a button instead of a keyboard paste.
 *
 * Browsers ask the user for clipboard access first and some cannot read images at all. In
 * every case that yields no image, the user is told why.
 */
export function useClipboardImage() {
  const i18n = useGlobalI18n();

  async function readImage(): Promise<File | null> {
    if (!navigator.clipboard?.read) {
      alert.warning(i18n.t("recipe.clipboard-unavailable"));
      return null;
    }

    try {
      for (const item of await navigator.clipboard.read()) {
        const type = item.types.find(t => t.startsWith("image/"));
        if (type) {
          return nameImage(new File([await item.getType(type)], "", { type }));
        }
      }
    }
    catch {
      alert.warning(i18n.t("recipe.clipboard-unavailable"));
      return null;
    }

    alert.warning(i18n.t("recipe.paste-no-image-found"));
    return null;
  }

  return { readImage };
}

/**
 * Hands the caller an image pasted from the clipboard (e.g. a screenshot).
 *
 * Pasting anything else is left alone, so text still pastes into fields as usual. If the
 * clipboard holds no image and nothing editable has focus, the user is told why nothing happened.
 */
export function usePasteImage({ onImage, enabled = true }: UsePasteImageOptions) {
  const i18n = useGlobalI18n();

  useEventListener(document, "paste", (event: ClipboardEvent) => {
    // A paste inside a dialog belongs to that dialog, not to the page behind it
    if (!toValue(enabled) || (event.target instanceof Element && event.target.closest(".v-overlay"))) {
      return;
    }

    const items = Array.from(event.clipboardData?.items ?? []);
    const image = items
      .find(item => item.kind === "file" && item.type.startsWith("image/"))
      ?.getAsFile();

    // Copying from a web page can put an image and its text on the clipboard together. In a
    // text field the text is what the user means to paste.
    const hasText = items.some(item => item.kind === "string" && ["text/plain", "text/html"].includes(item.type));

    if (image && !(hasText && isEditable(event.target))) {
      event.preventDefault();
      onImage(nameImage(image));
      return;
    }

    if (!isEditable(event.target)) {
      alert.warning(i18n.t("recipe.paste-no-image-found"));
    }
  });
}
