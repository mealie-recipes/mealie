import { OcrTsvResponse } from "~/lib/api/types/ocr";
import { Recipe } from "~/lib/api/types/recipe";

export type CanvasRect = {
  startX: number;
  startY: number;
  w: number;
  h: number;
};

export type ImagePosition = {
  sx: number;
  sy: number;
  sWidth: number;
  sHeight: number;
  dx: number;
  dy: number;
  dWidth: number;
  dHeight: number;
  scale: number;
  panStartPoint: {
    x: number;
    y: number;
  };
};

export type Mouse = {
  current: {
    x: number;
    y: number;
  };
  down: boolean;
};

// https://stackoverflow.com/questions/58434389/export typescript-deep-keyof-of-a-nested-object/58436959#58436959
type Prev = [never, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, ...0[]];

type Join<K, P> = K extends string | number
  ? P extends string | number
    ? `${K}${"" extends P ? "" : "."}${P}`
    : never
  : never;

export type Leaves<T, D extends number = 10> = [D] extends [never]
  ? never
  : T extends object
  ? { [K in keyof T]-?: Join<K, Leaves<T[K], Prev[D]>> }[keyof T]
  : "";

export type Paths<T, D extends number = 10> = [D] extends [never]
  ? never
  : T extends object
  ? {
      [K in keyof T]-?: K extends string | number ? `${K}` | Join<K, Paths<T[K], Prev[D]>> : never;
    }[keyof T]
  : "";

export type SelectedRecipeLeaves = Leaves<Recipe>;

export type CanvasModes = "selection" | "panAndZoom";

export type SelectedTextSplitModes = keyof OcrTsvResponse | "flatten";

export type ToolbarIcons<T extends string> = {
  sectionTitle: string;
  eventHandler(mode: T): void;
  highlight: T;
  icons: {
    name: T;
    icon: string;
    tooltip: string;
  }[];
}[];
