export interface SideBarLink {
  key?: string;
  icon: string;
  to?: string;
  href?: string;
  title: string;
  children?: SideBarLink[];
  childrenStartExpanded?: boolean;
  restricted: boolean;
}

export type SidebarLinks = Array<SideBarLink>;
