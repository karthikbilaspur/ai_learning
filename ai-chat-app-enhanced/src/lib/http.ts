export function jsonError(
  message: string,
  status = 500,
  extra?: Record<string, unknown>,
) {
  return Response.json(
    {
      error: message,
      ...extra,
    },
    {
      status,
    },
  );
}

export function getClientIp(
  request: Request,
): string {
  const forwardedFor =
    request.headers.get("x-forwarded-for");

  if (forwardedFor) {
    return (
      forwardedFor
        .split(",")[0]
        ?.trim() || "anonymous"
    );
  }

  return (
    request.headers.get("x-real-ip") ||
    "anonymous"
  );
}