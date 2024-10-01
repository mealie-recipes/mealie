// @ts-ignore missing color types
import Color from "@sphinxxxx/color-conversion";

const LIGHT_COLOR = "white";
const DARK_COLOR = "black";
const ACCESSIBILITY_THRESHOLD = 0.179;

/*
Function to pick the text color based on the background color.

Based on -> https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color
*/
export function getTextColor(bgColor: string | undefined): string {
  if (!bgColor) {
    return DARK_COLOR;
  }

  try {
    const color = new Color(bgColor);

    // if opacity is less than 0.3 always return dark color
    if (color._rgba[3] < 0.3) {
      return DARK_COLOR;
    }

    const uicolors = [color._rgba[0] / 255, color._rgba[1] / 255, color._rgba[2] / 255];
    const c = uicolors.map((col) => {
      if (col <= 0.03928) {
        return col / 12.92;
      }
      return Math.pow((col + 0.055) / 1.055, 2.4);
    });
    const L = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
    return L > ACCESSIBILITY_THRESHOLD ? DARK_COLOR : LIGHT_COLOR;
  } catch (error) {
    console.warn(error);
    return DARK_COLOR;
  }
}
