import { useContext } from "@nuxtjs/composition-api";
import { detectServerBaseUrl } from "../use-utils";

export const useStaticRoutes = () => {
  const { $config, req } = useContext();
  const serverBase = detectServerBaseUrl(req);

  const prefix = `${$config.SUB_PATH}/api`.replace("//", "/");

  const fullBase = serverBase + prefix;

  // Methods to Generate reference urls for assets/images *
  function recipeImage(recipeSlug: string, version = null, key = null) {
    return `${fullBase}/media/recipes/${recipeSlug}/images/original.webp?&rnd=${key}&version=${version}`;
  }

  function recipeSmallImage(recipeSlug: string, version = null, key = null) {
    return `${fullBase}/media/recipes/${recipeSlug}/images/min-original.webp?&rnd=${key}&version=${version}`;
  }

  function recipeTinyImage(recipeSlug: string, version = null, key = null) {
    return `${fullBase}/media/recipes/${recipeSlug}/images/tiny-original.webp?&rnd=${key}&version=${version}`;
  }

  function recipeAssetPath(recipeSlug: string, assetName: string) {
    return `${fullBase}/media/recipes/${recipeSlug}/assets/${assetName}`;
  }

  return {
    recipeImage,
    recipeSmallImage,
    recipeTinyImage,
    recipeAssetPath,
  };
};
