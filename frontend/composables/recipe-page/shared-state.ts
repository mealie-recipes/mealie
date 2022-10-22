import { computed, ComputedRef, ref, Ref, useContext } from "@nuxtjs/composition-api";
import { UserOut } from "~/lib/api/types/user";

export enum PageMode {
  EDIT = "EDIT",
  VIEW = "VIEW",
  COOK = "COOK",
}

export enum EditorMode {
  JSON = "JSON",
  FORM = "FORM",
}

/**
 * PageState encapsulates the state of the recipe page the can be shared across components.
 * It allows and facilitates the complex state management of the recipe page where many components
 * need to share and communicate with each other and guarantee consistency.
 *
 * **Page Modes**
 *
 * are ComputedRefs so we can use a readonly reactive copy of the state of the page.
 */
interface PageState {
  slug: Ref<string>;
  imageKey: Ref<number>;

  pageMode: ComputedRef<PageMode>;
  editMode: ComputedRef<EditorMode>;

  /**
   * true is the page is in edit mode and the edit mode is in form mode.
   */
  isEditForm: ComputedRef<boolean>;
  /**
   * true is the page is in edit mode and the edit mode is in json mode.
   */
  isEditJSON: ComputedRef<boolean>;
  /**
   * true is the page is in view mode.
   */
  isEditMode: ComputedRef<boolean>;
  /**
   * true is the page is in cook mode.
   */
  isCookMode: ComputedRef<boolean>;

  setMode: (v: PageMode) => void;
  setEditMode: (v: EditorMode) => void;
  toggleEditMode: () => void;
  toggleCookMode: () => void;
}

const memo: Record<string, PageState> = {};

function pageStateConstructor(slug: string): PageState {
  const slugRef = ref(slug);
  const pageModeRef = ref(PageMode.VIEW);
  const editModeRef = ref(EditorMode.FORM);

  const toggleEditMode = () => {
    if (editModeRef.value === EditorMode.FORM) {
      editModeRef.value = EditorMode.JSON;
      return;
    }
    editModeRef.value = EditorMode.FORM;
  };

  const toggleCookMode = () => {
    if (pageModeRef.value === PageMode.COOK) {
      pageModeRef.value = PageMode.VIEW;
      return;
    }
    pageModeRef.value = PageMode.COOK;
  };

  const setEditMode = (v: EditorMode) => {
    editModeRef.value = v;
  };

  const setMode = (toMode: PageMode) => {
    const fromMode = pageModeRef.value;

    if (fromMode === PageMode.EDIT && toMode === PageMode.VIEW) {
      setEditMode(EditorMode.FORM);
    }

    pageModeRef.value = toMode;
  };

  return {
    slug: slugRef,
    pageMode: computed(() => pageModeRef.value),
    editMode: computed(() => editModeRef.value),
    imageKey: ref(1),

    toggleEditMode,
    setMode,
    setEditMode,
    toggleCookMode,

    isEditForm: computed(() => {
      return pageModeRef.value === PageMode.EDIT && editModeRef.value === EditorMode.FORM;
    }),
    isEditJSON: computed(() => {
      return pageModeRef.value === PageMode.EDIT && editModeRef.value === EditorMode.JSON;
    }),
    isEditMode: computed(() => {
      return pageModeRef.value === PageMode.EDIT;
    }),
    isCookMode: computed(() => {
      return pageModeRef.value === PageMode.COOK;
    }),
  };
}

/**
 * usePageState provides a common way to interact with shared state across the
 * RecipePage component.
 */
export function usePageState(slug: string): PageState {
  if (!memo[slug]) {
    memo[slug] = pageStateConstructor(slug);
  }

  return memo[slug];
}

export function clearPageState(slug: string) {
  delete memo[slug];
}

/**
 * usePageUser provides a wrapper around $auth that provides a type-safe way to
 * access the UserOut type from the context. If no user is logged in then an empty
 * object with all properties set to their zero value is returned.
 */
export function usePageUser(): { user: UserOut } {
  const { $auth } = useContext();

  if (!$auth.user) {
    return {
      user: {
        id: "",
        group: "",
        groupId: "",
        cacheKey: "",
        email: "",
      },
    };
  }

  // @ts-expect-error - We know that the API always returns a UserOut, but I'm unsure how to type the $auth to know what type user is
  return { user: $auth.user as UserOut };
}
