/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface OpenAIIngredient {
  /**
   *
   * The input is simply the ingredient string you are processing as-is. It is forbidden to
   * modify this at all, you must provide the input exactly as you received it.
   *
   */
  input: string;
  /**
   *
   * This value is a float between 0 - 100, where 100 is full confidence that the result is correct,
   * and 0 is no confidence that the result is correct. If you're unable to parse anything,
   * and you put the entire string in the notes, you should return 0 confidence. If you can easily
   * parse the string into each component, then you should return a confidence of 100. If you have to
   * guess which part is the unit and which part is the food, your confidence should be lower, such as 60.
   * Even if there is no unit or note, if you're able to determine the food, you may use a higher confidence.
   * If the entire ingredient consists of only a food, you can use a confidence of 100.
   *
   */
  confidence?: number | null;
  /**
   *
   * The numerical representation of how much of this ingredient. For instance, if you receive
   * "3 1/2 grams of minced garlic", the quantity is "3 1/2". Quantity may be represented as a whole number
   * (integer), a float or decimal, or a fraction. You should output quantity in only whole numbers or
   * floats, converting fractions into floats. Floats longer than 10 decimal places should be
   * rounded to 10 decimal places.
   *
   */
  quantity?: number | null;
  /**
   *
   * The unit of measurement for this ingredient. For instance, if you receive
   * "2 lbs chicken breast", the unit is "lbs" (short for "pounds").
   *
   */
  unit?: string | null;
  /**
   *
   * The actual physical ingredient used in the recipe. For instance, if you receive
   * "3 cups of onions, chopped", the food is "onions".
   *
   */
  food?: string | null;
  /**
   *
   * The rest of the text that represents more detail on how to prepare the ingredient.
   * Anything that is not one of the above should be the note. For instance, if you receive
   * "one can of butter beans, drained" the note would be "drained". If you receive
   * "3 cloves of garlic peeled and finely chopped", the note would be "peeled and finely chopped".
   *
   */
  note?: string | null;
}
export interface OpenAIIngredients {
  ingredients?: OpenAIIngredient[];
}
export interface OpenAIBase {}
