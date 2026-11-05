import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick, ref } from "vue";
import RecipeNotes from "./RecipeNotes.vue";
import type { RecipeNote } from "~/lib/api/types/recipe";

const wrappers: VueWrapper[] = [];

function mountNotes(
  notes = ref<RecipeNote[]>([
    { referenceId: "note-1", title: "Note 1 Title", text: "Note 1 Text" },
    { referenceId: "note-2", title: "Note 2 Title", text: "Note 2 Text" },
  ]),
  edit = true,
) {
  const wrapper = mount(RecipeNotes, {
    props: {
      "modelValue": notes.value,
      "onUpdate:modelValue": (val: RecipeNote[]) => {
        notes.value = val;
      },
      "edit": edit,
    },
    global: {
      mocks: {
        $globals: {
          icons: {
            delete: "delete",
          },
        },
      },
      stubs: {
        BaseButton: {
          template: "<button class=\"base-button\"><slot /></button>",
        },
        SafeMarkdown: true,
        VCard: {
          template: "<div><slot /></div>",
        },
        VCardTitle: {
          template: "<div class=\"v-card-title\"><slot /></div>",
        },
        VCardText: {
          template: "<div class=\"v-card-text\"><slot /></div>",
        },
        VTextField: {
          props: ["modelValue"],
          emits: ["update:modelValue"],
          template: `<div class="v-text-field"><input :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" /></div>`,
        },
        VTextarea: {
          props: ["modelValue"],
          emits: ["update:modelValue"],
          template: `<div class="v-textarea"><textarea :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" /></div>`,
        },
        VIcon: true,
        VBtn: {
          template: "<button class=\"v-btn\"><slot /></button>",
        },
      },
    },
    attachTo: document.body,
  });

  wrappers.push(wrapper);
  return { wrapper, notes };
}

describe("RecipeNotes keyboard shortcuts", () => {
  beforeEach(() => {
    vi.stubGlobal("useNuxtApp", () => ({
      $globals: {
        icons: {
          delete: "delete",
        },
      },
    }));
  });

  afterEach(() => {
    wrappers.forEach(wrapper => wrapper.unmount());
    wrappers.length = 0;
    vi.unstubAllGlobals();
  });

  test("ctrl-enter on first note inserts a new note below and focuses its input", async () => {
    const { notes } = mountNotes();

    const firstNoteEl = document.querySelector("[data-note-id=\"note-1\"]");
    const input = firstNoteEl?.querySelector("input") as HTMLInputElement;
    expect(input).toBeTruthy();
    input.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(notes.value).toHaveLength(3);
    expect(notes.value[0].referenceId).toBe("note-1");
    expect(notes.value[2].referenceId).toBe("note-2");

    const newNoteId = notes.value[1].referenceId;
    const newNoteEl = document.querySelector(`[data-note-id="${newNoteId}"]`);
    const newInput = newNoteEl?.querySelector("input");
    expect(document.activeElement).toBe(newInput);
    expect(event.defaultPrevented).toBe(true);
  });

  test("meta-enter (Cmd+Enter) on note textarea inserts a new note below and focuses input", async () => {
    const { notes } = mountNotes();

    const firstNoteEl = document.querySelector("[data-note-id=\"note-1\"]");
    const textarea = firstNoteEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(notes.value).toHaveLength(3);
    expect(notes.value[0].referenceId).toBe("note-1");
    expect(notes.value[2].referenceId).toBe("note-2");
    expect(event.defaultPrevented).toBe(true);
  });

  test("ctrl-delete removes current note and focuses previous note input", async () => {
    const { notes } = mountNotes();

    const secondNoteEl = document.querySelector("[data-note-id=\"note-2\"]");
    const input = secondNoteEl?.querySelector("input") as HTMLInputElement;
    input.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Delete",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(notes.value).toHaveLength(1);
    expect(notes.value[0].referenceId).toBe("note-1");

    const prevNoteEl = document.querySelector("[data-note-id=\"note-1\"]");
    const prevInput = prevNoteEl?.querySelector("input");
    expect(document.activeElement).toBe(prevInput);
    expect(event.defaultPrevented).toBe(true);
  });

  test("ctrl-delete from textarea focuses previous note textarea", async () => {
    const { notes } = mountNotes();

    const secondNoteEl = document.querySelector("[data-note-id=\"note-2\"]");
    const textarea = secondNoteEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Delete",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(notes.value).toHaveLength(1);
    expect(notes.value[0].referenceId).toBe("note-1");

    const prevNoteEl = document.querySelector("[data-note-id=\"note-1\"]");
    const prevTextarea = prevNoteEl?.querySelector("textarea");
    expect(document.activeElement).toBe(prevTextarea);
    expect(event.defaultPrevented).toBe(true);
  });

  test("cmd-delete removes current note", async () => {
    const { notes } = mountNotes();

    const secondNoteEl = document.querySelector("[data-note-id=\"note-2\"]");
    const input = secondNoteEl?.querySelector("input") as HTMLInputElement;
    input.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Delete",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(notes.value).toHaveLength(1);
    expect(notes.value[0].referenceId).toBe("note-1");
    expect(event.defaultPrevented).toBe(true);
  });

  test("ctrl-arrow-up on second note swaps it with first note and refocuses active input", async () => {
    const { notes } = mountNotes();

    const secondNoteEl = document.querySelector("[data-note-id=\"note-2\"]");
    const input = secondNoteEl?.querySelector("input") as HTMLInputElement;
    input.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowUp",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(notes.value[0].referenceId).toBe("note-2");
    expect(notes.value[1].referenceId).toBe("note-1");

    const movedNoteEl = document.querySelector("[data-note-id=\"note-2\"]");
    const movedInput = movedNoteEl?.querySelector("input");
    expect(document.activeElement).toBe(movedInput);
    expect(event.defaultPrevented).toBe(true);
  });

  test("cmd-arrow-up moves note up", async () => {
    const { notes } = mountNotes();

    const secondNoteEl = document.querySelector("[data-note-id=\"note-2\"]");
    const textarea = secondNoteEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowUp",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(notes.value[0].referenceId).toBe("note-2");
    expect(notes.value[1].referenceId).toBe("note-1");

    const movedNoteEl = document.querySelector("[data-note-id=\"note-2\"]");
    const movedTextarea = movedNoteEl?.querySelector("textarea");
    expect(document.activeElement).toBe(movedTextarea);
    expect(event.defaultPrevented).toBe(true);
  });

  test("ctrl-arrow-down on first note swaps it with second note and refocuses active input", async () => {
    const { notes } = mountNotes();

    const firstNoteEl = document.querySelector("[data-note-id=\"note-1\"]");
    const input = firstNoteEl?.querySelector("input") as HTMLInputElement;
    input.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowDown",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(notes.value[0].referenceId).toBe("note-2");
    expect(notes.value[1].referenceId).toBe("note-1");

    const movedNoteEl = document.querySelector("[data-note-id=\"note-1\"]");
    const movedInput = movedNoteEl?.querySelector("input");
    expect(document.activeElement).toBe(movedInput);
    expect(event.defaultPrevented).toBe(true);
  });

  test("ctrl-arrow-up on top note is a no-op", async () => {
    const { notes } = mountNotes();

    const firstNoteEl = document.querySelector("[data-note-id=\"note-1\"]");
    const input = firstNoteEl?.querySelector("input") as HTMLInputElement;
    input.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowUp",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.dispatchEvent(event);
    await nextTick();

    expect(notes.value[0].referenceId).toBe("note-1");
    expect(notes.value[1].referenceId).toBe("note-2");
  });

  test("ctrl-arrow-down on bottom note is a no-op", async () => {
    const { notes } = mountNotes();

    const secondNoteEl = document.querySelector("[data-note-id=\"note-2\"]");
    const input = secondNoteEl?.querySelector("input") as HTMLInputElement;
    input.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowDown",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.dispatchEvent(event);
    await nextTick();

    expect(notes.value[0].referenceId).toBe("note-1");
    expect(notes.value[1].referenceId).toBe("note-2");
  });

  test("does nothing when edit mode is false", async () => {
    const { notes } = mountNotes(undefined, false);

    const firstNoteEl = document.querySelector("#note0");
    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    firstNoteEl?.dispatchEvent(event);
    await nextTick();

    expect(notes.value).toHaveLength(2);
    expect(event.defaultPrevented).toBe(false);
  });

  test("plain enter does not trigger insertion", async () => {
    const { notes } = mountNotes();

    const firstNoteEl = document.querySelector("[data-note-id=\"note-1\"]");
    const input = firstNoteEl?.querySelector("input") as HTMLInputElement;
    input.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      ctrlKey: false,
      metaKey: false,
      bubbles: true,
      cancelable: true,
    });
    input.dispatchEvent(event);
    await nextTick();

    expect(notes.value).toHaveLength(2);
    expect(event.defaultPrevented).toBe(false);
  });
});
