export interface SideBarLink {
  key?: string;
  icon: string;
  to?: string;
  href?: string;
  title: string;
  children?: SideBarLink[];
  childrenStartExpanded?: boolean;
  restricted: boolean;
  /** Shows a small colored square in place of the icon, as cookbooks do in the sidebar */
  color?: string;
  /** Shows a trailing count, e.g. the number of recipes in a cookbook */
  count?: number;
}

export type SidebarLinks = Array<SideBarLink>;
