import { reactive } from "@nuxtjs/composition-api";

interface Toast {
  open: boolean;
  text: string;
  title: string | null;
  color: string;
}

export const toastAlert = reactive<Toast>({
  open: false,
  title: null,
  text: "Hello From The Store",
  color: "info",
});

export const toastLoading = reactive<Toast>({
  open: false,
  title: null,
  text: "Importing Backup",
  color: "success",
});

function setToast(toast: Toast, text: string, title: string | null, color: string) {
  toast.open = true;
  toast.text = text;
  toast.title = title;
  toast.color = color;
}

export const loader = {
  info(text: string, title: string | null = null) {
    setToast(toastLoading, text, title, "info");
  },
  success(text: string, title: string | null = null) {
    setToast(toastLoading, text, title, "success");
  },
  error(text: string, title: string | null = null) {
    setToast(toastLoading, text, title, "error");
  },
  warning(text: string, title: string | null = null) {
    setToast(toastLoading, text, title, "warning");
  },
  close() {
    toastLoading.open = false;
  },
};

export const alert = {
  info(text: string, title: string | null = null) {
    setToast(toastAlert, text, title, "info");
  },
  success(text: string, title: string | null = null) {
    setToast(toastAlert, text, title, "success");
  },
  error(text: string, title: string | null = null) {
    setToast(toastAlert, text, title, "error");
  },
  warning(text: string, title: string | null = null) {
    setToast(toastAlert, text, title, "warning");
  },
  close() {
    toastAlert.open = false;
  },
};
