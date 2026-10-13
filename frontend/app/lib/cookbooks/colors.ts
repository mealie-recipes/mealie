// Muted swatches shown beside each cookbook, in the sidebar and on the cookbooks page,
// cycled through by the cookbook's position so a cookbook keeps its colour in both places
const COOKBOOK_COLORS = ["#d9a07e", "#a9b48a", "#c98f8f", "#8fa6b8", "#c7ad7a", "#a596b8"];

export function cookbookColor(index: number): string {
  return COOKBOOK_COLORS[Math.abs(index) % COOKBOOK_COLORS.length]!;
}
