import { recipeIngredient } from "./recipeIngredient";
import { recipeNumber } from "./recipeNumber";

export const ingredientScaler = {
  process(ingredientArray, scale) {
    console.log(scale);
    let workingArray = ingredientArray.map(x =>
      ingredientScaler.markIngredient(x)
    );
    return workingArray.map(x => ingredientScaler.adjustIngredients(x, scale));
  },

  adjustIngredients(ingredient, scale) {
    var scaledQuantity = new recipeNumber(ingredient.quantity).multiply(scale);
    const newText = ingredient.text.replace(
      ingredient.quantity,
      scaledQuantity
    );
    return { ...ingredient, quantity: scaledQuantity, text: newText };
  },

  markIngredient(ingredient) {
    console.log(ingredient);
    const returnVar = ingredient.replace(
      /^([\d/?[^\s&]*)(?:&nbsp;|\s)(\w*)/g,
      (match, quantity, unit) => {
        return `${unit}${quantity},${match}`;
      }
    );
    const split = returnVar.split(",");
    const [unit, quantity, match] = split;
    console.log("Split", unit, quantity, match);
    const n = new recipeNumber(quantity);
    const i = new recipeIngredient(n, unit);
    const serializedQuantity = n.isFraction() ? n.toImproperFraction() : n;
    return {
      unit: i,
      quantity: serializedQuantity.toString(),
      text: match,
    };
  },
};
