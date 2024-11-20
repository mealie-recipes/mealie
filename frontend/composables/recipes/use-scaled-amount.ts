import { useFraction } from "~/composables/recipes";

function formatQuantity(val: number): string {
  if (Number.isInteger(val)) {
    return val.toString();
  }

  const { frac } = useFraction();

  let valString = "";
  const fraction = frac(val, 10, true);

  if (fraction[0] !== undefined && fraction[0] > 0) {
      valString += fraction[0];
  }

  if (fraction[1] > 0) {
      valString += `<sup>${fraction[1]}</sup><span>&frasl;</span><sub>${fraction[2]}</sub>`;
  }

  return valString.trim();
}

export function useScaledAmount(amount: number, scale = 1) {
  const scaledAmount = Number(((amount || 0) * scale).toFixed(3));
  const scaledAmountDisplay = scaledAmount ? formatQuantity(scaledAmount) : "";

  return {
    scaledAmount,
    scaledAmountDisplay,
  };
}
