/**
 * v-no-autofill directive
 *
 * Vuetify 3 places data-* attributes on its wrapper div, not the underlying
 * <input> element, so password managers still offer to autofill. This directive
 * uses a MutationObserver to find and patch every <input> inside the host
 * element, even ones rendered asynchronously (dialogs, conditional blocks).
 *
 * From: https://github.com/vuetifyjs/vuetify/issues/18202
 *
 * Usage:
 *   <v-text-field v-no-autofill ... />
 *   <v-form v-no-autofill>...</v-form>
 *   <div v-no-autofill>...</div>
 */

import type { Directive, DirectiveBinding } from "vue";

interface ObservedElement extends HTMLElement {
  _noAutofillObserver?: MutationObserver;
}

function patchInput(input: HTMLInputElement) {
  input.setAttribute("autocomplete", "off");
  input.setAttribute("data-1p-ignore", "true");
  input.setAttribute("data-lpignore", "true");
  input.setAttribute("data-protonpass-ignore", "true");
  input.setAttribute("data-bwignore", "true");
  input.setAttribute("data-form-type", "other");
}

function patchAll(el: HTMLElement) {
  if (el.tagName === "INPUT") {
    patchInput(el as HTMLInputElement);
  }
  el.querySelectorAll<HTMLInputElement>("input").forEach(patchInput);
}

const noAutofill: Directive<ObservedElement> = {
  mounted(el: ObservedElement, _binding: DirectiveBinding) {
    patchAll(el);

    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            patchAll(node as HTMLElement);
          }
        }
      }
    });

    observer.observe(el, { childList: true, subtree: true });
    el._noAutofillObserver = observer;
  },

  unmounted(el: ObservedElement) {
    el._noAutofillObserver?.disconnect();
    delete el._noAutofillObserver;
  },
};

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive("no-autofill", noAutofill);
});
