export interface SideBarLink {
  key?: string;
  icon: string;
  to?: string;
  href?: string;
  title: string;
  children?: SideBarLink[];
  restricted: boolean;
}

export type SidebarLinks = Array<SideBarLink>;
