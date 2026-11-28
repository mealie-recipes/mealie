export const recipeSortOptions = [
  ["name", "asc", "name-ascending"], ["name", "desc", "name-descending"],
  ["created_at", "desc", "newest"], ["created_at", "asc", "oldest"],
  ["rating", "desc", "rating-descending"], ["rating", "asc", "rating-ascending"],
  ["total_time_seconds", "asc", "time-ascending"], ["total_time_seconds", "desc", "time-descending"],
  ["last_made", "desc", "made-descending"], ["last_made", "asc", "made-ascending"],
  ["updated_at", "desc", "updated-descending"], ["updated_at", "asc", "updated-ascending"],
  ["random", "desc", "random"],
] as const;
