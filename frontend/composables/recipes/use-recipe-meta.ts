import { Ref } from "@nuxtjs/composition-api";
import { useStaticRoutes } from "~/composables/api";
import { Recipe } from "~/lib/api/types/recipe";

export interface RecipeMeta {
  title?: string;
  mainImage?: string;
  meta: Array<any>;
  __dangerouslyDisableSanitizers: Array<string>;
  script: Array<any>;
}

export const useRecipeMeta = () => {
  const { recipeImage } = useStaticRoutes();
  function recipeMeta(recipe: Ref<Recipe | null>): RecipeMeta {
    const imageURL = recipeImage(recipe?.value?.id ?? "");
    return {
      title: recipe?.value?.name,
      mainImage: imageURL,
      meta: [
        { hid: "og:title", property: "og:title", content: recipe?.value?.name || "Recipe" },
        {
          hid: "og:description",
          property: "og:description",
          content: recipe?.value?.description ?? "",
        },
        {
          hid: "og:image",
          property: "og:image",
          content: imageURL,
        },
        {
          hid: "twitter:title",
          property: "twitter:title",
          content: recipe?.value?.name ?? "",
        },
        {
          hid: "twitter:desc",
          property: "twitter:description",
          content: recipe?.value?.description ?? "",
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
  }
  return { recipeMeta };
};
