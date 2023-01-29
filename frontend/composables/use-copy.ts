import { useContext } from "@nuxtjs/composition-api";
import { useClipboard } from "@vueuse/core";
import { alert } from "./use-toast";

export function useCopy() {
  const { copy, copied, isSupported } = useClipboard();
  const { i18n } = useContext();

  function copyText(text: string) {
    if (!isSupported) {
      alert.error(i18n.tc("general.clipboard-not-supported"));
      return;
    }
    copy(text);
    alert.success(i18n.tc("general.copied-to-clipboard"));
  }

  return { copyText, copied };
}

export function useCopyList() {
  const { copy, isSupported } = useClipboard();
  const { i18n } = useContext();

  function checkClipboard() {
    if (!isSupported) {
      alert.error(i18n.tc("general.your-browser-does-not-support-clipboard"));
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

    const text = list.map((item) => `- ${item}`).join("\n");
    copyText(text, list.length);
  }

  function copyMarkdownCheckList(list: string[]) {
    if (!checkClipboard()) return;

    const text = list.map((item) => `- [ ] ${item}`).join("\n");
    copyText(text, list.length);
  }

  function copyText(text: string, len: number) {
    copy(text).then(() => {
      alert.success(i18n.tc("general.copied-items-to-clipboard", len));
    });
  }

  return {
    copyPlain,
    copyMarkdown,
    copyMarkdownCheckList,
  };
}
