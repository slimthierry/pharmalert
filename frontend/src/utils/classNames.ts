/**
 * Utility to conditionally join class names.
 * Filters out falsy values and joins the rest with spaces.
 */
export function classNames(
  ...classes: (string | undefined | null | false)[]
): string {
  return classes.filter(Boolean).join(' ');
}
