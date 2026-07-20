const DEFAULT_API_URL = "http://127.0.0.1:8000/api";
const DEFAULT_TIMEOUT_MS = 15_000;

export const API_BASE_URL = (
  import.meta.env.VITE_API_URL || DEFAULT_API_URL
).replace(/\/+$/, "");


export class ApiError extends Error {
  constructor(message, options = {}) {
    super(message);

    this.name = "ApiError";
    this.status = options.status ?? 0;
    this.data = options.data ?? null;
  }
}


function buildUrl(path, query) {
  const normalizedPath = path.startsWith("/")
    ? path
    : `/${path}`;

  const url = new URL(
    `${API_BASE_URL}${normalizedPath}`,
  );

  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (
        value !== undefined
        && value !== null
        && value !== ""
      ) {
        url.searchParams.set(key, String(value));
      }
    });
  }

  return url;
}


async function parseResponseBody(response) {
  if (response.status === 204) {
    return null;
  }

  const responseText = await response.text();

  if (!responseText) {
    return null;
  }

  const contentType = response.headers.get(
    "content-type",
  );

  if (contentType?.includes("application/json")) {
    try {
      return JSON.parse(responseText);
    } catch {
      return null;
    }
  }

  return responseText;
}


function extractErrorMessage(data, status) {
  if (typeof data === "string" && data.trim()) {
    return data;
  }

  if (
    data
    && typeof data === "object"
    && typeof data.detail === "string"
  ) {
    return data.detail;
  }

  if (
    data
    && typeof data === "object"
    && Array.isArray(data.detail)
  ) {
    return data.detail
      .map((error) => {
        const field = Array.isArray(error.loc)
          ? error.loc.at(-1)
          : null;

        const message = error.msg || "Invalid value";

        return field
          ? `${field}: ${message}`
          : message;
      })
      .join(", ");
  }

  if (status === 404) {
    return "The requested resource was not found.";
  }

  if (status === 409) {
    return "The request conflicts with the current state.";
  }

  if (status === 422) {
    return "Some submitted values are invalid.";
  }

  if (status >= 500) {
    return "The ARGOS server could not process the request.";
  }

  return "The request could not be completed.";
}


export async function apiRequest(
  path,
  {
    method = "GET",
    query,
    body,
    headers,
    timeoutMs = DEFAULT_TIMEOUT_MS,
  } = {},
) {
  const controller = new AbortController();

  const timeoutId = window.setTimeout(() => {
    controller.abort();
  }, timeoutMs);

  const requestHeaders = new Headers(headers);

  if (body !== undefined) {
    requestHeaders.set(
      "Content-Type",
      "application/json",
    );
  }

  try {
    const response = await fetch(
      buildUrl(path, query),
      {
        method,
        headers: requestHeaders,
        body:
          body === undefined
            ? undefined
            : JSON.stringify(body),
        signal: controller.signal,
      },
    );

    const data = await parseResponseBody(response);

    if (!response.ok) {
      throw new ApiError(
        extractErrorMessage(data, response.status),
        {
          status: response.status,
          data,
        },
      );
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(
        "The request to the ARGOS API timed out.",
        {
          status: 408,
        },
      );
    }

    throw new ApiError(
      "Unable to connect to the ARGOS API.",
      {
        status: 0,
        data: error,
      },
    );
  } finally {
    window.clearTimeout(timeoutId);
  }
}


export const apiClient = {
  get(path, options = {}) {
    return apiRequest(path, {
      ...options,
      method: "GET",
    });
  },

  post(path, body, options = {}) {
    return apiRequest(path, {
      ...options,
      method: "POST",
      body,
    });
  },

  patch(path, body, options = {}) {
    return apiRequest(path, {
      ...options,
      method: "PATCH",
      body,
    });
  },

  delete(path, options = {}) {
    return apiRequest(path, {
      ...options,
      method: "DELETE",
    });
  },
};