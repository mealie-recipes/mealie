export interface RecommendationStatus {
  needsOnboarding: boolean;
  hasVector: boolean;
  ratingCount: number;
}

export interface RecommendationPreferencesIn {
  tags: string[];
}

export interface RecommendationDismissIn {
  recipeId: string;
}

export interface RecommendationItem {
  recipeId: string;
  slug?: string | null;
  name: string;
  description?: string | null;
  image?: string | null;
  rating?: number | null;
  tags?: string[];
  becauseTags?: string[];
  score?: number | null;
  rank?: number | null;
}

export interface RecommendationResult {
  recommendations: RecommendationItem[];
  coldStart: boolean;
  modelVersion: string;
}
