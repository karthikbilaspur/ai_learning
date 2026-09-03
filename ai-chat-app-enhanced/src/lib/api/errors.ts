export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(
    message: string,
    status = 500,
    code = "INTERNAL_ERROR",
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

export function badRequest(
  message: string,
) {
  return new ApiError(
    message,
    400,
    "BAD_REQUEST",
  );
}

export function unauthorized(
  message = "Authentication required",
) {
  return new ApiError(
    message,
    401,
    "UNAUTHORIZED",
  );
}

export function forbidden(
  message = "You do not have permission to access this resource",
) {
  return new ApiError(
    message,
    403,
    "FORBIDDEN",
  );
}

export function notFound(
  message = "Resource not found",
) {
  return new ApiError(
    message,
    404,
    "NOT_FOUND",
  );
}

export function isApiError(
  error: unknown,
): error is ApiError {
  return error instanceof ApiError;
}