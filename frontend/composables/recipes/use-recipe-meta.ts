import { Ref } from "@nuxtjs/composition-api";
import { useStaticRoutes } from "../api";
import { Recipe } from "~/types/api-types/recipe";

export const useRecipeMeta = (recipe: Ref<Recipe>) => {
  const { recipeImage } = useStaticRoutes();
  console.log(recipe.value);
  return () => {
    return {
      title: recipe?.value?.name || "Recipe",
      // @ts-ignore
      mainImage: recipeImage(recipe?.value?.image),
      meta: [
        { hid: "og:title", property: "og:title", content: recipe?.value?.name || "Recipe" },
        {
          hid: "og:desc",
          property: "og:description",
          content: recipe?.value?.description || "",
        },
        {
          hid: "og-image",
          property: "og:image",
          content: recipeImage(recipe?.value?.image || ""),
        },
        {
          hid: "twitter:title",
          property: "twitter:title",
          content: recipe?.value?.name || "Recipe",
        },
        {
          hid: "twitter:desc",
          property: "twitter:description",
          content: recipe?.value?.description || "",
        },
        { hid: "t-type", name: "twitter:card", content: "summary_large_image" },
      ],
      __dangerouslyDisableSanitizers: ["script"],
      script: [
        {
          innerHTML: JSON.stringify({
            "@context": "http://schema.org",
            "@type": "Recipe",
            ...recipe.value,
          }),
          type: "application/ld+json",
        },
      ],
    };
  };
};
