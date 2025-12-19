const flaggedWords = ["password", "mealie", "admin", "qwerty", "login"];

/**
 * scorePassword returns a score for a given password between 0 and 100.
 * if a password contains a flagged word, it returns 0.
 * @param pass
 * @returns
 */
export function scorePassword(pass: string): number {
  let score = 0;
  if (!pass) return score;

  if (pass.length < 6) return score;

  // Check for flagged words
  for (const word of flaggedWords) {
    if (pass.toLowerCase().includes(word)) {
      return 0;
    }
  }

  // award every unique letter until 5 repetitions
  const letters: { [key: string]: number } = {};

  for (let i = 0; i < pass.length; i++) {
    letters[pass[i]] = (letters[pass[i]] || 0) + 1;
    score += 5.0 / letters[pass[i]];
  }

  // bonus points for mixing it up
  const variations: { [key: string]: boolean } = {
    digits: /\d/.test(pass),
    lower: /[a-z]/.test(pass),
    upper: /[A-Z]/.test(pass),
    nonWords: /\W/.test(pass),
  };

  let variationCount = 0;
  for (const check in variations) {
    variationCount += variations[check] === true ? 1 : 0;
  }
  score += (variationCount - 1) * 10;

  return Math.max(Math.min(score, 100), 0);
}
