import { useStaticRoutes } from "~/composables/api";
import type { RecipeAsset } from "~/lib/api/types/recipe";

export interface LightboxItem {
  src: string;
  alt?: string;
  label?: string;
}

const IMAGE_EXTENSION_PATTERN = /\.(png|jpe?g|gif|webp|bmp|avif)$/i;

/** Whether a file name looks like an image, based on its extension. */
export function isImage(fileName?: string | null): boolean {
  if (!fileName) return false;
  return IMAGE_EXTENSION_PATTERN.test(fileName);
}

export interface BuildRecipeLightboxItemsArgs {
  heroUrl?: string | null;
  heroAlt?: string | null;
  assets?: RecipeAsset[] | null;
  assetUrl: (fileName: string) => string;
}

/**
 * Builds the ordered gallery list for the recipe lightbox: the hero image (if any) followed
 * by every image asset, in existing array order. Non-image assets (video, PDF, etc.) are
 * excluded entirely since the lightbox has no way to preview them.
 */
export function buildRecipeLightboxItems({ heroUrl, heroAlt, assets, assetUrl }: BuildRecipeLightboxItemsArgs): LightboxItem[] {
  const items: LightboxItem[] = [];

  if (heroUrl) {
    items.push({ src: heroUrl, alt: heroAlt ?? undefined });
  }

  (assets ?? [])
    .filter(asset => isImage(asset.fileName))
    .forEach((asset) => {
      const label = asset.name || asset.fileName || undefined;
      items.push({
        src: assetUrl(asset.fileName ?? ""),
        alt: label,
        label,
      });
    });

  return items;
}

/** Returns the index of the item whose src matches, or 0 if not found. */
export function findLightboxStartIndex(items: LightboxItem[], src: string): number {
  const index = items.findIndex(item => item.src === src);
  return index === -1 ? 0 : index;
}

export function canGoPrev(index: number): boolean {
  return index > 0;
}

export function canGoNext(index: number, total: number): boolean {
  return index < total - 1;
}

/**
 * Vue-facing wrapper around {@link buildRecipeLightboxItems} that binds the asset URL
 * builder to the app's configured static routes.
 */
export function useRecipeLightboxItems() {
  const { recipeAssetPath } = useStaticRoutes();

  function buildItems(recipeId: string, args: Omit<BuildRecipeLightboxItemsArgs, "assetUrl">): LightboxItem[] {
    return buildRecipeLightboxItems({
      ...args,
      assetUrl: fileName => recipeAssetPath(recipeId, fileName),
    });
  }

  return {
    buildItems,
  };
}
