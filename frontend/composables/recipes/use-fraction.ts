/* Loosely based on this Stackoverflow answer: https://stackoverflow.com/questions/14002113/how-to-simplify-a-decimal-into-the-smallest-possible-fraction#14011299 */

export function getLowestFraction(x: number) {
  const eps = 1.0E-06;
  let numerator, h1, h2, denominator, k1, k2, a;

  const whole = Math.floor(x);
  x = x - whole
  a = Math.floor(x);
  h1 = 1;
  k1 = 0;
  numerator = a;
  denominator = 1;

  while (x - a > eps * denominator * denominator) {
    x = 1 / (x - a);
    a = Math.floor(x);
    h2 = h1; h1 = numerator;
    k2 = k1; k1 = denominator;
    numerator = h2 + a * h1;
    denominator = k2 + a * k1;
  }

  return [whole, numerator, denominator];
}
