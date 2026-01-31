/**
 * Normalizes text by removing diacritics (accents) for search purposes.
 * This matches the backend normalization using unidecode.
 *
 * Example: "Käse" -> "kase", "Café" -> "cafe"
 */
export function normalizeText(text: string): string {
  if (!text) {
    return "";
  }

  // Normalize to NFD (decomposed form) and remove combining diacritical marks
  return text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

/**
 * Checks if a search term matches text, ignoring diacritics.
 */
export function matchesNormalized(searchTerm: string, text: string): boolean {
  const normalizedSearch = normalizeText(searchTerm);
  const normalizedText = normalizeText(text);
  return normalizedText.includes(normalizedSearch);
}
