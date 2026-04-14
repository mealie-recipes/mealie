import { useClipboard } from "@vueuse/core";
import { alert } from "./use-toast";

export function useCopy() {
  const { copy, copied, isSupported } = useClipboard();
  const i18n = useI18n();

  function copyText(text: string) {
    if (!isSupported.value) {
      alert.error(i18n.t("general.clipboard-not-supported"));
      return;
    }
    copy(text).then(() => {
      // Verify copy success as no error is thrown on failure.
      if (copied.value) {
        alert.success(i18n.t("general.copied-to-clipboard"));
      }
      else {
        alert.error(i18n.t("general.clipboard-copy-failure"));
      }
    });
  }

  return { copyText, copied };
}

export function useCopyList() {
  const { copy, isSupported, copied } = useClipboard();
  const i18n = useI18n();

  function checkClipboard() {
    if (!isSupported.value) {
      alert.error(i18n.t("general.your-browser-does-not-support-clipboard"));
      return false;
    }

    return true;
  }

  function copyPlain(list: string[]) {
    if (!checkClipboard()) return;

    const text = list.join("\n");
    copyText(text, list.length);
  }

  function copyMarkdown(list: string[]) {
    if (!checkClipboard()) return;

    const text = list.map(item => `- ${item}`).join("\n");
    copyText(text, list.length);
  }

  function copyMarkdownCheckList(list: string[]) {
    if (!checkClipboard()) return;

    const text = list.map(item => `- [ ] ${item}`).join("\n");
    copyText(text, list.length);
  }

  function copyText(text: string, len: number) {
    copy(text).then(() => {
      // Verify copy success as no error is thrown on failure.
      if (copied.value) {
        alert.success(i18n.t("general.copied-items-to-clipboard", len));
      }
      else {
        alert.error(i18n.t("general.clipboard-copy-failure"));
      }
    });
  }

  return {
    copyPlain,
    copyMarkdown,
    copyMarkdownCheckList,
  };
}
