import { describe, expect, test } from "vitest";
import {
  buildRecipeLightboxItems,
  canGoNext,
  canGoPrev,
  findLightboxStartIndex,
  isImage,
} from "../use-recipe-lightbox-items";
import type { RecipeAsset } from "~/lib/api/types/recipe";

const assetUrl = (fileName: string) => `/api/media/assets/${fileName}`;

describe("isImage", () => {
  test.each(["photo.png", "photo.JPG", "photo.jpeg", "photo.gif", "photo.webp", "photo.bmp", "photo.avif"])(
    "returns true for image extension %s",
    (fileName) => {
      expect(isImage(fileName)).toBe(true);
    },
  );

  test.each(["video.mp4", "doc.pdf", "notes.json", "archive.zip"])(
    "returns false for non-image extension %s",
    (fileName) => {
      expect(isImage(fileName)).toBe(false);
    },
  );

  test("returns false when file name is missing", () => {
    expect(isImage(undefined)).toBe(false);
    expect(isImage(null)).toBe(false);
    expect(isImage("")).toBe(false);
  });
});

describe("buildRecipeLightboxItems", () => {
  const imageAsset: RecipeAsset = { name: "Plated dish", icon: "mdi-file-image", fileName: "plated.jpg" };
  const unnamedImageAsset: RecipeAsset = { name: "", icon: "mdi-file-image", fileName: "raw.png" };
  const videoAsset: RecipeAsset = { name: "Cooking video", icon: "mdi-file", fileName: "clip.mp4" };
  const pdfAsset: RecipeAsset = { name: "Recipe card", icon: "mdi-file-pdf-box", fileName: "card.pdf" };

  test("hero followed by image assets in existing order, hero has no label", () => {
    const items = buildRecipeLightboxItems({
      heroUrl: "/api/media/recipes/1/images/original.webp",
      heroAlt: "My Recipe",
      assets: [imageAsset, videoAsset, unnamedImageAsset],
      assetUrl,
    });

    expect(items).toEqual([
      { src: "/api/media/recipes/1/images/original.webp", alt: "My Recipe" },
      { src: "/api/media/assets/plated.jpg", alt: "Plated dish", label: "Plated dish" },
      { src: "/api/media/assets/raw.png", alt: "raw.png", label: "raw.png" },
    ]);
  });

  test("no hero image results in assets-only list", () => {
    const items = buildRecipeLightboxItems({
      heroUrl: null,
      heroAlt: "My Recipe",
      assets: [imageAsset],
      assetUrl,
    });

    expect(items).toEqual([
      { src: "/api/media/assets/plated.jpg", alt: "Plated dish", label: "Plated dish" },
    ]);
  });

  test("non-image assets (video, pdf) are excluded", () => {
    const items = buildRecipeLightboxItems({
      heroUrl: null,
      assets: [videoAsset, pdfAsset],
      assetUrl,
    });

    expect(items).toEqual([]);
  });

  test("falls back to fileName for label when asset name is empty", () => {
    const items = buildRecipeLightboxItems({
      heroUrl: null,
      assets: [{ name: "", icon: "mdi-file-image", fileName: "untitled.png" }],
      assetUrl,
    });

    expect(items[0].label).toBe("untitled.png");
    expect(items[0].alt).toBe("untitled.png");
  });

  test("handles missing assets array", () => {
    const items = buildRecipeLightboxItems({
      heroUrl: "/hero.webp",
      assetUrl,
    });

    expect(items).toEqual([{ src: "/hero.webp", alt: undefined }]);
  });
});

describe("findLightboxStartIndex", () => {
  const items = [
    { src: "/hero.webp" },
    { src: "/asset-a.png", label: "A" },
    { src: "/asset-b.png", label: "B" },
  ];

  test("returns the index of the matching item", () => {
    expect(findLightboxStartIndex(items, "/asset-b.png")).toBe(2);
  });

  test("returns 0 when no item matches", () => {
    expect(findLightboxStartIndex(items, "/does-not-exist.png")).toBe(0);
  });
});

describe("canGoPrev / canGoNext", () => {
  test("first item can only go next", () => {
    expect(canGoPrev(0)).toBe(false);
    expect(canGoNext(0, 3)).toBe(true);
  });

  test("last item can only go prev", () => {
    expect(canGoPrev(2)).toBe(true);
    expect(canGoNext(2, 3)).toBe(false);
  });

  test("middle item can go both directions", () => {
    expect(canGoPrev(1)).toBe(true);
    expect(canGoNext(1, 3)).toBe(true);
  });

  test("single item list can go neither direction", () => {
    expect(canGoPrev(0)).toBe(false);
    expect(canGoNext(0, 1)).toBe(false);
  });
});
