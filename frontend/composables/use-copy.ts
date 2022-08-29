import { useClipboard } from "@vueuse/core";
import { alert } from "./use-toast";

export function useCopy() {
  const { copy, copied, isSupported } = useClipboard();

  function copyText(text: string) {
    if (!isSupported) {
      alert.error("Clipboard not supported");
      return;
    }
    copy(text);
    alert.success("Copied to clipboard");
  }

  return { copyText, copied };
}

export function useCopyList() {
  const { copy, isSupported } = useClipboard();

  function checkClipboard() {
    if (!isSupported) {
      alert.error("Your browser does not support clipboard");
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
      alert.success(`Copied ${len} items to clipboard`);
    });
  }

  return {
    copyPlain,
    copyMarkdown,
    copyMarkdownCheckList,
  };
}
