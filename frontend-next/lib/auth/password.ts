const flaggedWords = ["password", "mealie", "admin", "qwerty", "login"];

/**
 * Compute a strength score for a password on a scale from 0 to 100.
 *
 * @param pass - The password to evaluate.
 * @returns The numeric strength score in the range 0–100. Returns `0` if the password is empty, shorter than 6 characters, or contains a flagged word; larger values indicate stronger passwords.
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
