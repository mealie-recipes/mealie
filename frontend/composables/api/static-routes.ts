import { useContext } from "@nuxtjs/composition-api";
import { detectServerBaseUrl } from "../use-utils";

function UnknownToString(ukn: string | unknown) {
  return typeof ukn === "string" ? ukn : "";
}

export const useStaticRoutes = () => {
  const { $config, req } = useContext();
  const serverBase = detectServerBaseUrl(req);

  const prefix = `${$config.SUB_PATH as string}/api`.replace("//", "/");

  const fullBase = serverBase + prefix;

  // Methods to Generate reference urls for assets/images *
  function recipeImage(recipeId: string, version: string | unknown = "", key: string | number = 1) {
    return `${fullBase}/media/recipes/${recipeId}/images/original.webp?rnd=${key}&version=${UnknownToString(version)}`;
  }

  function recipeSmallImage(recipeId: string, version: string | unknown = "", key: string | number = 1) {
    return `${fullBase}/media/recipes/${recipeId}/images/min-original.webp?rnd=${key}&version=${UnknownToString(
      version
    )}`;
  }

  function recipeTinyImage(recipeId: string, version: string | unknown = "", key: string | number = 1) {
    return `${fullBase}/media/recipes/${recipeId}/images/tiny-original.webp?rnd=${key}&version=${UnknownToString(
      version
    )}`;
  }

  function recipeAssetPath(recipeId: string, assetName: string) {
    return `${fullBase}/media/recipes/${recipeId}/assets/${assetName}`;
  }

  return {
    recipeImage,
    recipeSmallImage,
    recipeTinyImage,
    recipeAssetPath,
  };
};
