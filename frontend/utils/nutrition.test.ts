import { describe, expect, test } from "vitest";
import {
  toNum,
  round,
  getRecipeServings,
  perOneServing,
  scaleForServings,
  sumMacros,
} from "./nutrition";
import type { Recipe } from "~/lib/api/types/recipe";

describe("nutrition utilities", () => {
  describe("toNum", () => {
    test("converts numbers", () => {
      expect(toNum(42)).toBe(42);
      expect(toNum(3.14)).toBe(3.14);
    });

    test("converts string numbers", () => {
      expect(toNum("42")).toBe(42);
      expect(toNum("3.14")).toBe(3.14);
    });

    test("extracts numbers from strings", () => {
      expect(toNum("4 Portionen")).toBe(4);
      expect(toNum("2.5 servings")).toBe(2.5);
      expect(toNum("Makes 8")).toBe(8);
    });

    test("handles null/undefined/empty", () => {
      expect(toNum(null)).toBe(0);
      expect(toNum(undefined)).toBe(0);
      expect(toNum("")).toBe(0);
    });

    test("handles invalid strings", () => {
      expect(toNum("no number here")).toBe(0);
    });
  });

  describe("round", () => {
    test("rounds to specified decimals", () => {
      expect(round(3.14159, 0)).toBe(3);
      expect(round(3.14159, 1)).toBe(3.1);
      expect(round(3.14159, 2)).toBe(3.14);
    });

    test("handles edge cases", () => {
      expect(round(0, 1)).toBe(0);
      expect(round(2.5, 0)).toBe(3); // Rounds up
    });
  });

  describe("getRecipeServings", () => {
    test("uses recipeServings first", () => {
      const recipe = {
        recipeServings: 4,
        recipeYieldQuantity: 8,
        recipeYield: "12",
      } as Recipe;
      expect(getRecipeServings(recipe)).toBe(4);
    });

    test("uses recipeYieldQuantity if recipeServings missing", () => {
      const recipe = {
        recipeYieldQuantity: 6,
        recipeYield: "12",
      } as Recipe;
      expect(getRecipeServings(recipe)).toBe(6);
    });

    test("parses recipeYield string if numbers missing", () => {
      const recipe = {
        recipeYield: "8 Portionen",
      } as Recipe;
      expect(getRecipeServings(recipe)).toBe(8);
    });

    test("defaults to 1 if all missing", () => {
      const recipe = {} as Recipe;
      expect(getRecipeServings(recipe)).toBe(1);
    });

    test("defaults to 1 if recipeYield unparseable", () => {
      const recipe = {
        recipeYield: "some text",
      } as Recipe;
      expect(getRecipeServings(recipe)).toBe(1);
    });
  });

  describe("perOneServing", () => {
    test("normalizes nutrition for multi-serving recipe", () => {
      const recipe = {
        recipeServings: 4,
        nutrition: {
          calories: "800",
          proteinContent: "40",
          fatContent: "20",
          carbohydrateContent: "80",
        },
      } as Recipe;

      const result = perOneServing(recipe);
      expect(result.calories).toBe(200); // 800 / 4
      expect(result.protein).toBe(10); // 40 / 4
      expect(result.fat).toBe(5); // 20 / 4
      expect(result.carbohydrate).toBe(20); // 80 / 4
    });

    test("handles single serving recipe", () => {
      const recipe = {
        recipeServings: 1,
        nutrition: {
          calories: "650",
          proteinContent: "30",
          fatContent: "25",
          carbohydrateContent: "50",
        },
      } as Recipe;

      const result = perOneServing(recipe);
      expect(result.calories).toBe(650);
      expect(result.protein).toBe(30);
      expect(result.fat).toBe(25);
      expect(result.carbohydrate).toBe(50);
    });

    test("handles missing nutrition", () => {
      const recipe = {
        recipeServings: 4,
      } as Recipe;

      const result = perOneServing(recipe);
      expect(result.calories).toBe(0);
      expect(result.protein).toBe(0);
      expect(result.fat).toBe(0);
      expect(result.carbohydrate).toBe(0);
    });

    test("handles partial nutrition data", () => {
      const recipe = {
        recipeServings: 2,
        nutrition: {
          calories: "600",
          // Missing protein, fat, carbs
        },
      } as Recipe;

      const result = perOneServing(recipe);
      expect(result.calories).toBe(300); // 600 / 2
      expect(result.protein).toBe(0);
      expect(result.fat).toBe(0);
      expect(result.carbohydrate).toBe(0);
    });
  });

  describe("scaleForServings", () => {
    test("scales nutrition values", () => {
      const perServing = {
        calories: 200,
        protein: 10,
        fat: 5,
        carbohydrate: 20,
        carbs: 20,
      };

      const result = scaleForServings(perServing, 2);
      expect(result.calories).toBe(400);
      expect(result.protein).toBe(20);
      expect(result.fat).toBe(10);
      expect(result.carbohydrate).toBe(40);
    });

    test("handles fractional servings", () => {
      const perServing = {
        calories: 300,
        protein: 15,
        fat: 10,
        carbohydrate: 30,
        carbs: 30,
      };

      const result = scaleForServings(perServing, 0.5);
      expect(result.calories).toBe(150);
      expect(result.protein).toBe(7.5);
      expect(result.fat).toBe(5);
      expect(result.carbohydrate).toBe(15);
    });

    test("handles zero servings", () => {
      const perServing = {
        calories: 200,
        protein: 10,
        fat: 5,
        carbohydrate: 20,
        carbs: 20,
      };

      const result = scaleForServings(perServing, 0);
      expect(result.calories).toBe(0);
      expect(result.protein).toBe(0);
      expect(result.fat).toBe(0);
      expect(result.carbohydrate).toBe(0);
    });
  });

  describe("sumMacros", () => {
    test("sums multiple macro objects", () => {
      const items = [
        { calories: 200, protein: 10, fat: 5, carbohydrate: 20, carbs: 20 },
        { calories: 300, protein: 15, fat: 10, carbohydrate: 30, carbs: 30 },
        { calories: 150, protein: 8, fat: 3, carbohydrate: 15, carbs: 15 },
      ];

      const result = sumMacros(items);
      expect(result.calories).toBe(650);
      expect(result.protein).toBe(33);
      expect(result.fat).toBe(18);
      expect(result.carbohydrate).toBe(65);
    });

    test("handles empty array", () => {
      const result = sumMacros([]);
      expect(result.calories).toBe(0);
      expect(result.protein).toBe(0);
      expect(result.fat).toBe(0);
      expect(result.carbohydrate).toBe(0);
    });

    test("handles single item", () => {
      const items = [
        { calories: 500, protein: 25, fat: 15, carbohydrate: 50, carbs: 50 },
      ];

      const result = sumMacros(items);
      expect(result.calories).toBe(500);
      expect(result.protein).toBe(25);
      expect(result.fat).toBe(15);
      expect(result.carbohydrate).toBe(50);
    });
  });

  describe("integration: full workflow", () => {
    test("Test case 1 from spec: Recipe A (800kcal, 4 servings) x2 + Recipe B (650kcal) x1", () => {
      const recipeA = {
        recipeServings: 4,
        nutrition: {
          calories: "800",
          proteinContent: "40",
          fatContent: "20",
          carbohydrateContent: "80",
        },
      } as Recipe;

      const recipeB = {
        recipeServings: 1,
        nutrition: {
          calories: "650",
          proteinContent: "30",
          fatContent: "25",
          carbohydrateContent: "50",
        },
      } as Recipe;

      // Recipe A: per serving = 800/4 = 200 kcal, then x2 = 400
      const perA = perOneServing(recipeA);
      expect(perA.calories).toBe(200);
      const scaledA = scaleForServings(perA, 2);
      expect(scaledA.calories).toBe(400);

      // Recipe B: per serving = 650, then x1 = 650
      const perB = perOneServing(recipeB);
      expect(perB.calories).toBe(650);
      const scaledB = scaleForServings(perB, 1);
      expect(scaledB.calories).toBe(650);

      // Total = 400 + 650 = 1050
      const total = sumMacros([scaledA, scaledB]);
      expect(total.calories).toBe(1050);
    });

    test("Test case 2 from spec: Recipe without nutrition -> 0 kcal", () => {
      const recipeC = {
        recipeServings: 2,
      } as Recipe;

      const per = perOneServing(recipeC);
      expect(per.calories).toBe(0);

      const scaled = scaleForServings(per, 1);
      expect(scaled.calories).toBe(0);
    });
  });
});
