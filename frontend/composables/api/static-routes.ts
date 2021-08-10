import { useContext } from "@nuxtjs/composition-api";

export const useStaticRoutes = () => {
  const { $config } = useContext();

  const prefix = `${$config.SUB_PATH}/api`.replace("//", "/");

  // Methods to Generate reference urls for assets/images *
  function recipeImage(recipeSlug: string, version = null, key = null) {
    return `${prefix}/media/recipes/${recipeSlug}/images/original.webp?&rnd=${key}&version=${version}`;
  }

  function recipeSmallImage(recipeSlug: string, version = null, key = null) {
    return `${prefix}/media/recipes/${recipeSlug}/images/min-original.webp?&rnd=${key}&version=${version}`;
  }

  function recipeTinyImage(recipeSlug: string, version = null, key = null) {
    return `${prefix}/media/recipes/${recipeSlug}/images/tiny-original.webp?&rnd=${key}&version=${version}`;
  }

  function recipeAssetPath(recipeSlug: string, assetName: string) {
    return `${prefix}/media/recipes/${recipeSlug}/assets/${assetName}`;
  }

  return {
    recipeImage,
    recipeSmallImage,
    recipeTinyImage,
    recipeAssetPath,
  };
};
