export function clamp(
  value: number,
  min: number,
  max: number,
): number {
  return Math.min(
    Math.max(value, min),
    max,
  );
}

export function truncate(
  value: string,
  maxLength: number,
): string {
  if (value.length <= maxLength) {
    return value;
  }

  return `${value.slice(
    0,
    Math.max(0, maxLength - 1),
  )}…`;
}