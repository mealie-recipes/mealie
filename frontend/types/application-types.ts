import { TranslateResult } from "vue-i18n";

export interface SideBarLink {
    icon: string
    to: string
    title: TranslateResult
}

export type SidebarLinks = Array<SideBarLink>