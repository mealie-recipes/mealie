export interface ContextMenuItem {
  title: string;
  icon: string;
  event: string;
  color?: string;
}

export interface ContextMenuPresets {
  delete: ContextMenuItem;
  edit: ContextMenuItem;
  save: ContextMenuItem;
}

export function useContextPresets(): ContextMenuPresets {
  const i18n = useI18n();
  const { $globals } = useNuxtApp();

  return {
    delete: {
      title: i18n.t("general.delete"),
      icon: $globals.icons.delete,
      event: "delete",
    },
    edit: {
      title: i18n.t("general.edit"),
      icon: $globals.icons.edit,
      event: "edit",
    },
    save: {
      title: i18n.t("general.save"),
      icon: $globals.icons.save,
      event: "save",
    },
  };
}
