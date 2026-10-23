export function textColorForBackground(color: string | undefined | null) {
  const hex = /^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$/.exec(color ?? "")?.[1];
  if (!hex) {
    return undefined;
  }

  const expanded =
    hex.length === 3
      ? hex
          .split("")
          .map((c) => c + c)
          .join("")
      : hex;
  const r = parseInt(expanded.slice(0, 2), 16);
  const g = parseInt(expanded.slice(2, 4), 16);
  const b = parseInt(expanded.slice(4, 6), 16);
  const yiq = (r * 299 + g * 587 + b * 114) / 1000;
  return yiq >= 140 ? "#000000" : "#ffffff";
}
