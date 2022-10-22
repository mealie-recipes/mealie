import { TranslateResult } from "vue-i18n/types";

export interface SideBarLink {
  icon: string;
  to?: string;
  href?: string;
  title: TranslateResult;
  children?: SideBarLink[];
}

export type SidebarLinks = Array<SideBarLink>;
