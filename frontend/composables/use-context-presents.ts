import { useContext } from "@nuxtjs/composition-api";

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
  const { $globals, i18n } = useContext();

  return {
    delete: {
      title: i18n.tc("general.delete"),
      icon: $globals.icons.delete,
      event: "delete",
    },
    edit: {
      title: i18n.tc("general.edit"),
      icon: $globals.icons.edit,
      event: "edit",
    },
    save: {
      title: i18n.tc("general.save"),
      icon: $globals.icons.save,
      event: "save",
    },
  };
}
