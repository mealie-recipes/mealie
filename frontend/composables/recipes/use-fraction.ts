/* frac.js (C) 2012-present SheetJS -- http://sheetjs.com */
/* https://developer.aliyun.com/mirror/npm/package/frac/v/0.3.0 Apache license */

function frac(x: number, D: number, mixed: boolean) {
  let n1 = Math.floor(x);
  let d1 = 1;
  let n2 = n1 + 1;
  let d2 = 1;
  if (x !== n1)
    while (d1 <= D && d2 <= D) {
      const m = (n1 + n2) / (d1 + d2);
      if (x === m) {
        if (d1 + d2 <= D) {
          d1 += d2;
          n1 += n2;
          d2 = D + 1;
        } else if (d1 > d2) d2 = D + 1;
        else d1 = D + 1;
        break;
      } else if (x < m) {
        n2 = n1 + n2;
        d2 = d1 + d2;
      } else {
        n1 = n1 + n2;
        d1 = d1 + d2;
      }
    }
  if (d1 > D) {
    d1 = d2;
    n1 = n2;
  }
  if (!mixed) return [0, n1, d1];
  const q = Math.floor(n1 / d1);
  return [q, n1 - q * d1, d1];
}
function cont(x: number, D: number, mixed: boolean) {
  const sgn = x < 0 ? -1 : 1;
  let B = x * sgn;
  let P_2 = 0;
  let P_1 = 1;
  let P = 0;
  let Q_2 = 1;
  let Q_1 = 0;
  let Q = 0;
  let A = Math.floor(B);
  while (Q_1 < D) {
    A = Math.floor(B);
    P = A * P_1 + P_2;
    Q = A * Q_1 + Q_2;
    if (B - A < 0.00000005) break;
    B = 1 / (B - A);
    P_2 = P_1;
    P_1 = P;
    Q_2 = Q_1;
    Q_1 = Q;
  }
  if (Q > D) {
    if (Q_1 > D) {
      Q = Q_2;
      P = P_2;
    } else {
      Q = Q_1;
      P = P_1;
    }
  }
  if (!mixed) return [0, sgn * P, Q];
  const q = Math.floor((sgn * P) / Q);
  return [q, sgn * P - q * Q, Q];
}

export const useFraction = function () {
  return {
    frac,
    cont,
  };
};
