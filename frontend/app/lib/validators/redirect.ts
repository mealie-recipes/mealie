// rejects protocol-relative payloads (`//evil.com`, `/\evil.com`) that a bare startsWith("/") check would miss
export function isSafeRedirectTarget(target: string | null | undefined): target is string {
  return !!target && target.startsWith("/") && !/^[/\\]{2}/.test(target);
}
