export const RECIPE_PHOTO_ACCEPT = ".avif,.bmp,.gif,.jpeg,.jpg,.png,.webp";

export function isRecipePhoto(fileName?: string | null): boolean {
  return !!fileName && /\.(avif|bmp|gif|jpe?g|png|webp)$/i.test(fileName);
}
