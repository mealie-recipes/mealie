function UnknownToString(ukn: string | unknown) {
  return typeof ukn === "string" ? ukn : "";
}

export const useStaticRoutes = () => {
  const { $config } = useNuxtApp();
  const serverBase = useRequestURL().origin;

  const prefix = `${$config.public.SUB_PATH}/api`.replace("//", "/");

  const fullBase = serverBase + prefix;

  // Methods to Generate reference urls for assets/images *
  function recipeImage(recipeId: string, version: string | unknown = "", key: string | number = 1) {
    return `${fullBase}/media/recipes/${recipeId}/images/original.webp?rnd=${key}&version=${UnknownToString(version)}`;
  }

  function recipeSmallImage(recipeId: string, version: string | unknown = "", key: string | number = 1) {
    return `${fullBase}/media/recipes/${recipeId}/images/min-original.webp?rnd=${key}&version=${UnknownToString(
      version,
    )}`;
  }

  function recipeTinyImage(recipeId: string, version: string | unknown = "", key: string | number = 1) {
    return `${fullBase}/media/recipes/${recipeId}/images/tiny-original.webp?rnd=${key}&version=${UnknownToString(
      version,
    )}`;
  }

  function recipeTimelineEventImage(recipeId: string, timelineEventId: string) {
    return `${fullBase}/media/recipes/${recipeId}/images/timeline/${timelineEventId}/original.webp`;
  }

  function recipeTimelineEventSmallImage(recipeId: string, timelineEventId: string) {
    return `${fullBase}/media/recipes/${recipeId}/images/timeline/${timelineEventId}/min-original.webp`;
  }

  function recipeTimelineEventTinyImage(recipeId: string, timelineEventId: string) {
    return `${fullBase}/media/recipes/${recipeId}/images/timeline/${timelineEventId}/tiny-original.webp`;
  }

  function recipeAssetPath(recipeId: string, assetName: string) {
    return `${fullBase}/media/recipes/${recipeId}/assets/${assetName}`;
  }

  return {
    recipeImage,
    recipeSmallImage,
    recipeTinyImage,
    recipeTimelineEventImage,
    recipeTimelineEventSmallImage,
    recipeTimelineEventTinyImage,
    recipeAssetPath,
  };
};
